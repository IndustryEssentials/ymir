# Copyright (c) 2017-present, Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################
#
# Based on:
# --------------------------------------------------------
# Fast/er R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Bharath Hariharan
# --------------------------------------------------------
"""Python implementation of the PASCAL VOC devkit's AP evaluation code."""

from typing import Any, Dict, List, Optional

import numpy as np

from mir.protos import mir_command_pb2 as mirpb
from mir.tools.eval import eval_utils


def _voc_ap(rec: np.ndarray, prec: np.ndarray, use_07_metric: bool) -> float:
    """Compute VOC AP given precision and recall. If use_07_metric is true, uses
    the VOC 07 11-point method (default:False).
    """
    if use_07_metric:
        # 11 point metric
        ap = 0.
        for t in np.arange(0., 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])
            ap = ap + p / 11.
    else:
        # correct AP calculation
        # first append sentinel values at the end
        mrec: np.ndarray = np.concatenate(([0.], rec, [1.]))  # type: ignore
        mpre: np.ndarray = np.concatenate(([0.], prec, [0.]))  # type: ignore

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]  # type: ignore

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def _voc_eval(class_recs: Dict[str, Dict[str, Any]], BB: np.ndarray, confidence: np.ndarray, image_ids: List[str],
              pred_pb_index_ids: List[int], match_result: eval_utils.DetEvalMatchResult, ovthresh: float, npos: int,
              use_07_metric: bool) -> Dict[str, Any]:
    """
    gt: class_recs
    pred: BB, confidence, image_ids, pred_pb_index_ids
    """
    if len(image_ids) == 0:
        return {
            'rec': [],
            'prec': [],
            'conf': [],
            'ap': 0,
            'ar': 0,
            'tp': 0,
            'fp': 0,
            'fn': 0,
        }

    # `BB` and `image_ids`: sort desc by confidence
    sorted_ind = np.argsort(-confidence)
    BB = BB[sorted_ind, :]
    image_ids = [image_ids[x] for x in sorted_ind]
    pred_pb_index_ids = [pred_pb_index_ids[x] for x in sorted_ind]

    # go down dets and mark TPs and FPs
    nd = len(image_ids)
    tp = np.zeros(nd)  # 0 or 1, tp[d] == 1 means BB[d] is true positive
    fp = np.zeros(nd)  # 0 or 1, tp[d] == 1 means BB[d] is false positive
    for d in range(nd):
        if image_ids[d] not in class_recs:
            fp[d] = 1.
            continue

        R = class_recs[image_ids[d]]  # gt of that image name
        bb = BB[d, :].astype(float)  # single prediction box, shape: (1, 4)
        ovmax = -np.inf
        BBGT: np.ndarray = R['bbox'].astype(float)  # gt boxes of that image name, shape: (*, 4), x1, y1, x2, y2

        if BBGT.size > 0:
            # compute overlaps
            # intersection
            ixmin = np.maximum(BBGT[:, 0], bb[0])
            iymin = np.maximum(BBGT[:, 1], bb[1])
            ixmax = np.minimum(BBGT[:, 2], bb[2])
            iymax = np.minimum(BBGT[:, 3], bb[3])
            iw = np.maximum(ixmax - ixmin + 1., 0.)
            ih = np.maximum(iymax - iymin + 1., 0.)
            inters = iw * ih

            # union
            area1 = (bb[2] - bb[0] + 1.) * (bb[3] - bb[1] + 1.)
            area2 = (BBGT[:, 2] - BBGT[:, 0] + 1.) * (BBGT[:, 3] - BBGT[:, 1] + 1.)
            uni = (area1 + area2 - inters)

            overlaps = inters / uni
            ovmax = np.max(overlaps)
            jmax = np.argmax(overlaps)

        if ovmax > ovthresh:
            if not R['difficult'][jmax]:
                if not R['det'][jmax]:
                    # pred `d` matched to gt `jmax`
                    tp[d] = 1.
                    R['det'][jmax] = 1

                    match_result.add_match(asset_id=image_ids[d],
                                           iou_thr=ovthresh,
                                           gt_pb_idx=class_recs[image_ids[d]]['pb_index_ids'][jmax],
                                           pred_pb_idx=pred_pb_index_ids[d])
                else:
                    # jmax previously matched to another
                    fp[d] = 1.
        else:
            # pred `d` not matched to anything
            fp[d] = 1.

    # compute precision recall
    fp = np.cumsum(fp)
    tp = np.cumsum(tp)
    rec = tp / float(npos)  # recalls
    prec = tp / np.maximum(tp + fp, np.finfo(np.float64).eps)  # precisions
    ap: float = _voc_ap(rec, prec, use_07_metric)

    tp_cnt = int(tp[-1]) if len(tp) > 0 else 0
    fp_cnt = int(fp[-1]) if len(fp) > 0 else 0
    fn_cnt = npos - tp_cnt

    return {
        'rec': rec,
        'prec': prec,
        'conf': confidence[sorted_ind],
        'ap': ap,
        'ar': np.mean(rec),
        'tp': tp_cnt,
        'fp': fp_cnt,
        'fn': fn_cnt,
    }


def _get_single_evaluate_element(prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations,
                                 match_result: eval_utils.DetEvalMatchResult, class_id: int, iou_thr: float,
                                 conf_thr: float, need_pr_curve: bool) -> mirpb.SingleEvaluationElement:
    # convert data structure
    # convert gt, save to `class_recs`
    class_recs: Dict[str, Dict[str, Any]] = {}
    npos = 0
    for asset_id, image_annotations in ground_truth.image_annotations.items():
        img_gts = [x for x in image_annotations.boxes if x.class_id == class_id]

        # bbox: shape: (len(annos), 4), type: int, x1y1x2y2
        bbox = np.array([[x.box.x, x.box.y, x.box.x + x.box.w, x.box.y + x.box.h] for x in img_gts])
        difficult = np.array([False] * len(img_gts))  # shape: (len(annos),)
        det = [False] * len(img_gts)  # 1: have matched detections, 0: not matched yet
        if len(difficult) > 0:
            npos = npos + sum(~difficult)
        pb_index_ids = [x.index for x in img_gts]

        class_recs[asset_id] = {
            'bbox': bbox,
            'difficult': difficult,
            'det': det,
            'pb_index_ids': pb_index_ids,
        }

    # convert det
    image_ids: List[str] = []
    confidence = []
    bboxes: List[List[int]] = []
    pred_pb_index_ids: List[int] = []
    for asset_id, image_annotations in prediction.image_annotations.items():
        img_preds = [x for x in image_annotations.boxes if x.class_id == class_id and x.score > conf_thr]
        for annotation in img_preds:
            box = annotation.box
            bboxes.append([box.x, box.y, box.x + box.w, box.y + box.h])
        image_ids.extend([asset_id] * len(img_preds))
        confidence.extend([x.score for x in img_preds])
        pred_pb_index_ids.extend([x.index for x in img_preds])
    BB = np.array(bboxes)

    # voc eval
    # matches: set to save match result, each element: (asset_id, gt_pb_index, pred_pb_index)
    eval_result = _voc_eval(class_recs=class_recs,
                            BB=BB,
                            confidence=np.array(confidence),
                            image_ids=image_ids,
                            pred_pb_index_ids=pred_pb_index_ids,
                            match_result=match_result,
                            ovthresh=iou_thr,
                            npos=npos,
                            use_07_metric=False)

    # voc_eval to get result
    see = mirpb.SingleEvaluationElement(ap=eval_result['ap'],
                                        ar=eval_result['ar'],
                                        tp=eval_result['tp'],
                                        fp=eval_result['fp'],
                                        fn=eval_result['fn'])

    if need_pr_curve:
        rec = eval_result['rec']
        prec = eval_result['prec']
        conf = eval_result['conf']

        for i in range(len(rec)):
            see.pr_curve.append(mirpb.FloatPoint(x=rec[i], y=prec[i], z=conf[i]))

    return see


def evaluate(prediction: mirpb.SingleTaskAnnotations,
             ground_truth: mirpb.SingleTaskAnnotations,
             config: mirpb.EvaluateConfig,
             assets_metadata: Optional[mirpb.MirMetadatas] = None) -> mirpb.Evaluation:
    evaluation = mirpb.Evaluation()
    evaluation.config.CopyFrom(config)

    class_ids = list(config.class_ids)
    iou_thrs = eval_utils.get_iou_thrs_array(config.iou_thrs_interval)

    single_dataset_evaluation = evaluation.dataset_evaluation
    single_dataset_evaluation.conf_thr = config.conf_thr

    for iou_thr in iou_thrs:
        match_result = eval_utils.DetEvalMatchResult()
        for class_id in class_ids:
            see = _get_single_evaluate_element(prediction=prediction,
                                               ground_truth=ground_truth,
                                               class_id=class_id,
                                               iou_thr=iou_thr,
                                               conf_thr=config.conf_thr,
                                               need_pr_curve=config.need_pr_curve,
                                               match_result=match_result)
            single_dataset_evaluation.iou_evaluations[f"{iou_thr:.2f}"].ci_evaluations[class_id].CopyFrom(see)

        eval_utils.write_instance_confusion_matrix(gt_annotations=ground_truth,
                                                   pred_annotations=prediction,
                                                   class_ids=class_ids,
                                                   conf_thr=config.conf_thr,
                                                   match_result=match_result,
                                                   iou_thr=iou_thrs[0])
    eval_utils.calc_averaged_evaluations(dataset_evaluation=single_dataset_evaluation, class_ids=class_ids)

    evaluation.state = mirpb.EvaluationState.ES_READY
    return evaluation
