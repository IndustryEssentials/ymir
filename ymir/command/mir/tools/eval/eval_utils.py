from collections import defaultdict
from typing import Collection, Dict, List, Set, Tuple

import numpy as np

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


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

    def get_asset_ids(self, iou_thr: float) -> Collection[str]:
        return self._iou_matches[iou_thr].gt_pred_match.keys() if iou_thr in self._iou_matches else []

    def get_matches(self, asset_id: str, iou_thr: float) -> Collection[Tuple[int, int]]:
        return self._iou_matches[iou_thr].gt_pred_match[asset_id]


def get_iou_thrs_array(iou_thrs_str: str) -> np.ndarray:
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


def calc_averaged_evaluations(dataset_evaluation: mirpb.SingleDatasetEvaluation, class_ids: Collection[int]) -> None:
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


def write_semantic_confusion_matrix(gt_annotations: mirpb.SingleTaskAnnotations,
                                    pred_annotations: mirpb.SingleTaskAnnotations,
                                    class_ids: List[int], match_result: Dict[str, List[int]]) -> None:
    for asset_id, image_annotations in gt_annotations.image_annotations.items():
        match_class_ids = match_result.get(asset_id, [])
        for annotation in image_annotations.boxes:
            if annotation.class_id in match_class_ids:
                annotation.cm = mirpb.ConfusionMatrixType.MTP
            elif annotation.class_id in class_ids:
                annotation.cm = mirpb.ConfusionMatrixType.FN
            else:
                annotation.cm = mirpb.ConfusionMatrixType.IGNORED
            annotation.det_link_id = -1
    for asset_id, image_annotations in pred_annotations.image_annotations.items():
        match_class_ids = match_result.get(asset_id, [])
        for annotation in image_annotations.boxes:
            if annotation.class_id in match_class_ids:
                annotation.cm = mirpb.ConfusionMatrixType.TP
            elif annotation.class_id in class_ids:
                annotation.cm = mirpb.ConfusionMatrixType.FP
            else:
                annotation.cm = mirpb.ConfusionMatrixType.IGNORED
            annotation.det_link_id = -1


def write_instance_confusion_matrix(gt_annotations: mirpb.SingleTaskAnnotations,
                                    pred_annotations: mirpb.SingleTaskAnnotations, class_ids: List[int],
                                    conf_thr: float, match_result: DetEvalMatchResult, iou_thr: float) -> None:
    class_ids_set = set(class_ids)
    for image_annotations in gt_annotations.image_annotations.values():
        for annotation in image_annotations.boxes:
            annotation.cm = (mirpb.ConfusionMatrixType.FN
                             if annotation.class_id in class_ids_set else mirpb.ConfusionMatrixType.IGNORED)
            annotation.det_link_id = -1
    for image_annotations in pred_annotations.image_annotations.values():
        for annotation in image_annotations.boxes:
            annotation.cm = (mirpb.ConfusionMatrixType.FP if annotation.class_id in class_ids_set
                             and annotation.score >= conf_thr else mirpb.ConfusionMatrixType.IGNORED)
            annotation.det_link_id = -1

    for asset_id in match_result.get_asset_ids(iou_thr=iou_thr):
        # exclude impossible matches
        if asset_id not in gt_annotations.image_annotations or asset_id not in pred_annotations.image_annotations:
            continue

        id_to_gts = {box.index: box for box in gt_annotations.image_annotations[asset_id].boxes}
        id_to_preds = {box.index: box for box in pred_annotations.image_annotations[asset_id].boxes}

        for gt_pb_index, pred_pb_index in match_result.get_matches(asset_id=asset_id, iou_thr=iou_thr):
            id_to_gts[gt_pb_index].cm = mirpb.ConfusionMatrixType.MTP
            id_to_gts[gt_pb_index].det_link_id = pred_pb_index
            id_to_preds[pred_pb_index].cm = mirpb.ConfusionMatrixType.TP
            id_to_preds[pred_pb_index].det_link_id = gt_pb_index
