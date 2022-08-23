from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import numpy as np

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


class MirDataset:
    def __init__(self,
                 mir_metadatas: mirpb.MirMetadatas,
                 mir_annotations: mirpb.MirAnnotations,
                 mir_keywords: mirpb.MirKeywords,
                 conf_thr: float,
                 dataset_id: str,
                 as_gt: bool,
                 asset_ids: Iterable[str] = None) -> None:
        """
        creates MirDataset instance

        Args:
            mir_metadatas (mirpb.MirMetadatas): metadatas
            mir_annotations (mirpb.MirAnnotations): annotations
            mir_keywords (mirpb.MirKeywords): keywords
            conf_thr (float): lower bound of annotation confidence score
            as_gt (bool): if false, use preds in mir_annotations and mir_keywords, if true, use gt
            asset_ids (Iterable[str]): asset ids you want to include in MirDataset instance, None means include all
        """
        task_annotations = mir_annotations.ground_truth if as_gt else mir_annotations.prediction
        keyword_to_idx = mir_keywords.gt_idx if as_gt else mir_keywords.pred_idx

        if len(mir_metadatas.attributes) == 0:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='no assets in evaluated dataset')
        if len(task_annotations.image_annotations) == 0:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_NO_ANNOTATIONS,
                                  error_message='no annotations in evaluated dataset')

        # ordered list of asset / image ids
        self._ordered_asset_ids = sorted(asset_ids or mir_metadatas.attributes.keys())
        # key: asset id, value: index in `self._ordered_asset_ids`
        self._asset_id_to_ordered_idxes = {asset_id: idx for idx, asset_id in enumerate(self._ordered_asset_ids)}
        # ordered list of class / category ids
        self._ordered_class_ids = sorted(list(keyword_to_idx.cis.keys()))
        self._ck_idx: Dict[str, mirpb.AssetAnnoIndex] = {key: value for key, value in mir_keywords.ck_idx.items()}

        self.img_cat_to_annotations: Dict[Tuple[int, int], List[dict]] = defaultdict(list)
        annos = self._get_annotations(single_task_annotations=task_annotations,
                                      asset_idxes=self.get_asset_idxes(),
                                      class_ids=self.get_class_ids(),
                                      conf_thr=None if as_gt else conf_thr)
        for anno in annos:
            self.img_cat_to_annotations[anno['asset_idx'], anno['class_id']].append(anno)

        self._task_annotations = task_annotations

        self._dataset_id = dataset_id

    @property
    def ck_idx(self) -> Dict[str, mirpb.AssetAnnoIndex]:
        return self._ck_idx

    @property
    def asset_id_to_ordered_idxes(self) -> Dict[str, int]:
        return self._asset_id_to_ordered_idxes

    @property
    def dataset_id(self) -> str:
        return self._dataset_id

    def _get_annotations(self, single_task_annotations: mirpb.SingleTaskAnnotations, asset_idxes: List[int],
                         class_ids: List[int], conf_thr: Optional[float]) -> List[dict]:
        """
        get all annotations list for asset ids and class ids

        if asset_idxes and class_ids provided, only returns filtered annotations

        Args:
            single_task_annotations (mirpb.SingleTaskAnnotations): annotations
            asset_idxes (List[int]): asset ids, if not provided, returns annotations for all images
            class_ids (List[int]): class ids, if not provided, returns annotations for all classe
            conf_thr (float): confidence threshold of bbox, set to None if you want all annotations

        Returns:
            a list of annotations and asset ids
            each element is a dict, and has following keys and values:
                asset_id: str, image / asset id
                asset_idx: int, position of asset id in `self.get_asset_ids()`
                id: int, id for a single annotation
                class_id: int, category / class id
                area: int, area of bbox
                bbox: List[int], bounding box, xywh
                score: float, confidence of bbox
                iscrowd: always 0 because mir knows nothing about it
        """
        result_annotations_list: List[dict] = []

        if not asset_idxes:
            asset_idxes = self.get_asset_idxes()

        annotation_idx = 1
        for asset_idx in asset_idxes:
            asset_id = self._ordered_asset_ids[asset_idx]
            if asset_id not in single_task_annotations.image_annotations:
                continue

            single_image_annotations = single_task_annotations.image_annotations[asset_id]
            for annotation in single_image_annotations.annotations:
                if class_ids and annotation.class_id not in class_ids:
                    continue
                if conf_thr is not None and annotation.score < conf_thr:
                    continue

                annotation_dict = {
                    'asset_id': asset_id,
                    'asset_idx': asset_idx,
                    'id': annotation_idx,
                    'class_id': annotation.class_id,
                    'area': annotation.box.w * annotation.box.h,
                    'bbox': [annotation.box.x, annotation.box.y, annotation.box.w, annotation.box.h],
                    'score': annotation.score,
                    'iscrowd': 0,
                    'ignore': 0,
                    'cm': {},  # key: (iou_thr_idx, maxDet), value: (ConfusionMatrixType, linked pb_index_id)
                    'pb_index_id': annotation.index,
                }
                result_annotations_list.append(annotation_dict)

                annotation_idx += 1

        return result_annotations_list

    def get_asset_ids(self) -> List[str]:
        return self._ordered_asset_ids

    def get_asset_idxes(self) -> List[int]:
        return list(range(len(self._ordered_asset_ids)))

    def get_class_ids(self) -> List[int]:
        return self._ordered_class_ids


class _DetEvalIouMatchResult:
    def __init__(self) -> None:
        self._gt_pred_match: Dict[str, Set[Tuple[int, int]]] = defaultdict(set)

    def add_match(self, asset_id: str, gt_pb_idx: int, pred_pb_idx: int) -> None:
        self._gt_pred_match[asset_id].add((gt_pb_idx, pred_pb_idx))

    @property
    def gt_pred_match(self) -> Dict[str, Set[Tuple[int, int]]]:
        return self._gt_pred_match


class DetEvalMatchResult:
    def __init__(self) -> None:
        self._iou_matches: Dict[float, _DetEvalIouMatchResult] = defaultdict(_DetEvalIouMatchResult)

    def add_match(self, asset_id: str, iou_thr: float, gt_pb_idx: int, pred_pb_idx: int) -> None:
        self._iou_matches[iou_thr].add_match(asset_id=asset_id, gt_pb_idx=gt_pb_idx, pred_pb_idx=pred_pb_idx)

    def get_asset_ids(self, iou_thr: float) -> Iterable[str]:
        return self._iou_matches[iou_thr].gt_pred_match.keys() if iou_thr in self._iou_matches else []

    def get_matches(self, asset_id: str, iou_thr: float) -> Iterable[Tuple[int, int]]:
        return self._iou_matches[iou_thr].gt_pred_match[asset_id]


def get_ious_array(iou_thrs_str: str) -> np.ndarray:
    iou_thrs = [float(v) for v in iou_thrs_str.split(':')]
    if len(iou_thrs) == 3:
        iou_thr_from, iou_thr_to, iou_thr_step = iou_thrs
    elif len(iou_thrs) == 1:
        iou_thr_from, iou_thr_to, iou_thr_step = iou_thrs[0], iou_thrs[0], 0
    else:
        raise ValueError(f"invalid iou thrs str: {iou_thrs_str}")
    for thr in [iou_thr_from, iou_thr_to, iou_thr_step]:
        if thr < 0 or thr > 1:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='invalid iou_thr_from, iou_thr_to or iou_thr_step')
    if iou_thr_from > iou_thr_to:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='invalid iou_thr_from or iou_thr_to')

    if iou_thr_to == iou_thr_from:
        return np.array([iou_thr_from])
    return np.linspace(start=iou_thr_from,
                       stop=iou_thr_to,
                       num=int(np.round((iou_thr_to - iou_thr_from) / iou_thr_step)),
                       endpoint=False)


def calc_averaged_evaluations(dataset_evaluation: mirpb.SingleDatasetEvaluation, class_ids: Iterable[int]) -> None:
    for iou_evaluation in dataset_evaluation.iou_evaluations.values():
        _get_average_ee(average_ee=iou_evaluation.ci_averaged_evaluation,
                        ees=list(iou_evaluation.ci_evaluations.values()))

    for class_id in class_ids:
        _get_average_ee(average_ee=dataset_evaluation.iou_averaged_evaluation.ci_evaluations[class_id],
                        ees=[x.ci_evaluations[class_id] for x in dataset_evaluation.iou_evaluations.values()])

    _get_average_ee(average_ee=dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation,
                    ees=[x.ci_averaged_evaluation for x in dataset_evaluation.iou_evaluations.values()])


def _get_average_ee(average_ee: mirpb.SingleEvaluationElement, ees: List[mirpb.SingleEvaluationElement]) -> None:
    if not ees:
        return

    if len(ees) == 1:
        average_ee.CopyFrom(ees[0])
        del average_ee.pr_curve[:]
        return

    for ee in ees:
        average_ee.ap += ee.ap
        average_ee.ar += ee.ar
        average_ee.tp += ee.tp
        average_ee.fp += ee.fp
        average_ee.fn += ee.fn

    ees_cnt = len(ees)
    average_ee.ap /= ees_cnt
    average_ee.ar /= ees_cnt


def _erase_confusion_matrix(gt_annotations: mirpb.SingleTaskAnnotations, pred_annotations: mirpb.SingleTaskAnnotations,
                            class_ids: Iterable[int]) -> None:
    class_ids_set = set(class_ids)

    for image_annotations in gt_annotations.image_annotations.values():
        for annotation in image_annotations.annotations:
            annotation.cm = (mirpb.ConfusionMatrixType.FN
                             if annotation.class_id in class_ids_set else mirpb.ConfusionMatrixType.IGNORED)
            annotation.det_link_id = -1
    for image_annotations in pred_annotations.image_annotations.values():
        for annotation in image_annotations.annotations:
            annotation.cm = (mirpb.ConfusionMatrixType.FP
                             if annotation.class_id in class_ids_set else mirpb.ConfusionMatrixType.IGNORED)
            annotation.det_link_id = -1


def reset_default_confusion_matrix(task_annotations: mirpb.SingleTaskAnnotations, cm: Any) -> None:
    for image_annotations in task_annotations.image_annotations.values():
        for annotation in image_annotations.annotations:
            annotation.cm = cm
            annotation.det_link_id = -1


def write_confusion_matrix(mir_gt: MirDataset, mir_dt: MirDataset, class_ids: List[int],
                           match_result: DetEvalMatchResult, iou_thr: float) -> None:
    gt_annotations = mir_gt._task_annotations
    pred_annotations = mir_dt._task_annotations

    # TODO: change to reset_default_confusion_matrix
    _erase_confusion_matrix(gt_annotations=gt_annotations, pred_annotations=pred_annotations, class_ids=class_ids)

    for asset_id in match_result.get_asset_ids(iou_thr=iou_thr):
        for gt_pb_index, pred_pb_index in match_result.get_matches(asset_id=asset_id, iou_thr=iou_thr):
            gt_annotations.image_annotations[asset_id].annotations[gt_pb_index].cm = mirpb.ConfusionMatrixType.MTP
            gt_annotations.image_annotations[asset_id].annotations[gt_pb_index].det_link_id = pred_pb_index
            pred_annotations.image_annotations[asset_id].annotations[pred_pb_index].cm = mirpb.ConfusionMatrixType.TP
            pred_annotations.image_annotations[asset_id].annotations[pred_pb_index].det_link_id = gt_pb_index
