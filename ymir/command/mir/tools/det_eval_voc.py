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

from typing import Any, Dict, List

import numpy as np

from mir.protos import mir_command_pb2 as mirpb
from mir.tools.det_eval_utils import calc_averaged_evaluations, get_ious_array, MirDataset
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def _voc_ap(rec, prec, use_07_metric=False):
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
        mrec = np.concatenate(([0.], rec, [1.]))
        mpre = np.concatenate(([0.], prec, [0.]))

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def _voc_eval(class_recs, BB, confidence, image_ids, ovthresh, npos, use_07_metric) -> Dict[str, Any]:
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

    # go down dets and mark TPs and FPs
    nd = len(image_ids)
    tp = np.zeros(nd)  # 0 or 1, tp[d] == 1 means BB[d] is true positive
    fp = np.zeros(nd)  # 0 or 1, tp[d] == 1 means BB[d] is false positive
    for d in range(nd):
        if image_ids[d] not in class_recs:
            continue  # TODO: should i continue here?

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
            uni = ((bb[2] - bb[0] + 1.) * (bb[3] - bb[1] + 1.) + (BBGT[:, 2] - BBGT[:, 0] + 1.) *
                   (BBGT[:, 3] - BBGT[:, 1] + 1.) - inters)

            overlaps = inters / uni
            ovmax = np.max(overlaps)
            jmax = np.argmax(overlaps)

        if ovmax > ovthresh:
            if not R['difficult'][jmax]:
                if not R['det'][jmax]:
                    tp[d] = 1.
                    R['det'][jmax] = 1
                else:
                    fp[d] = 1.
        else:
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
    # TODO: tp/mtp/fp/fn tags


def _get_single_evaluate_element(mir_dt: MirDataset, mir_gt: MirDataset, class_id: int, iou_thr: float,
                                 need_pr_curve: bool) -> mirpb.SingleEvaluationElement:
    # convert data structure
    # convert gt, save to `class_recs`
    class_recs: Dict[int, Dict[str, Any]] = {}
    npos = 0
    for asset_idx in mir_gt.get_asset_idxes():
        if (asset_idx, class_id) not in mir_gt.img_cat_to_annotations:
            continue

        annos: List[dict] = mir_gt.img_cat_to_annotations[(asset_idx, class_id)]
        bbox = np.array([x['bbox'] for x in annos])  # shape: (len(annos), 4), type: int
        bbox[:, 2] += bbox[:, 0]  # w -> x2
        bbox[:, 3] += bbox[:, 1]  # h -> y2
        difficult = np.array([x['iscrowd'] for x in annos]).astype(bool)  # shape: (len(annos),), type: int
        det = [False] * len(annos)  # 1: have matched detections, 0: not matched yet
        npos = npos + sum(~difficult)
        class_recs[asset_idx] = {'bbox': bbox, 'difficult': difficult, 'det': det}

    # convert det
    image_ids = []
    confidence = []
    bboxes: List[List[int]] = []
    for asset_idx in mir_dt.get_asset_idxes():
        annos: List[dict] = mir_dt.img_cat_to_annotations[(asset_idx, class_id)] if (
            asset_idx, class_id) in mir_dt.img_cat_to_annotations else []
        for anno in annos:
            bbox = anno['bbox']
            bboxes.append([bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]])
        image_ids.extend([asset_idx] * len(annos))
        confidence.extend([float(x['score']) for x in annos])
    BB = np.array(bboxes)

    # voc eval
    eval_result = _voc_eval(class_recs=class_recs,
                            BB=BB,
                            confidence=np.array(confidence),
                            image_ids=image_ids,
                            ovthresh=iou_thr,
                            npos=npos,
                            use_07_metric=True)

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


def det_evaluate(mir_dts: List[MirDataset], mir_gt: MirDataset, config: mirpb.EvaluateConfig) -> mirpb.Evaluation:
    if config.conf_thr < 0 or config.conf_thr > 1:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid conf_thr')

    evaluation = mirpb.Evaluation()
    evaluation.config.CopyFrom(config)

    class_ids = mir_gt.get_class_ids()
    iou_thrs = get_ious_array(config.iou_thrs_interval)

    for mir_dt in mir_dts:
        dataset_evaluation = evaluation.dataset_evaluations[mir_dt.dataset_id]
        for iou_thr in iou_thrs:
            for class_id in class_ids:
                dataset_evaluation.iou_evaluations[f"{iou_thr:.2f}"].ci_evaluations[class_id].CopyFrom(
                    _get_single_evaluate_element(mir_dt=mir_dt,
                                                 mir_gt=mir_gt,
                                                 class_id=class_id,
                                                 iou_thr=iou_thr,
                                                 need_pr_curve=config.need_pr_curve))
        calc_averaged_evaluations(dataset_evaluation=dataset_evaluation, class_ids=class_ids)

    return evaluation
