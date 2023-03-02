from typing import Tuple

from mir.tools.eval import eval_coco
from mir.protos import mir_command_pb2 as mirpb


def _make_box_eval_params_copy(
    prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations, config: mirpb.EvaluateConfig
) -> Tuple[mirpb.SingleTaskAnnotations, mirpb.SingleTaskAnnotations, mirpb.EvaluateConfig]:
    """
    copy to avoid unexpected change
    """
    copy_config = mirpb.EvaluateConfig()
    copy_config.CopyFrom(config)
    copy_config.type = mirpb.ObjectType.OT_DET_BOX
    copy_prediction = mirpb.SingleTaskAnnotations()
    copy_prediction.CopyFrom(prediction)
    copy_ground_truth = mirpb.SingleTaskAnnotations()
    copy_ground_truth.CopyFrom(ground_truth)
    return copy_prediction, copy_ground_truth, copy_config


def _re_arrange_evaluation_element(seg_ee: mirpb.SingleEvaluationElement,
                                   box_ee: mirpb.SingleEvaluationElement) -> None:
    seg_ee.maskAP = seg_ee.ap
    seg_ee.boxAP = box_ee.ap
    seg_ee.ap = 0


def evaluate(prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations,
             config: mirpb.EvaluateConfig, assets_metadata: mirpb.MirMetadatas) -> mirpb.Evaluation:
    # calc boxAP
    copy_prediction, copy_ground_truth, copy_config = _make_box_eval_params_copy(prediction, ground_truth, config)
    box_evaluation = eval_coco.evaluate(prediction=copy_prediction,
                                        ground_truth=copy_ground_truth,
                                        config=copy_config,
                                        assets_metadata=assets_metadata)

    # calc maskAP
    seg_evaluation = eval_coco.evaluate(prediction=prediction,
                                        ground_truth=ground_truth,
                                        config=config,
                                        assets_metadata=assets_metadata)

    # re-arrange results
    for iou_thr, sie in seg_evaluation.dataset_evaluation.iou_evaluations.items():
        for ci, ee in sie.ci_evaluations.items():
            _re_arrange_evaluation_element(
                seg_ee=ee, box_ee=box_evaluation.dataset_evaluation.iou_evaluations[iou_thr].ci_evaluations[ci])
        _re_arrange_evaluation_element(
            seg_ee=sie.ci_averaged_evaluation,
            box_ee=box_evaluation.dataset_evaluation.iou_evaluations[iou_thr].ci_averaged_evaluation)
    for ci, ee in seg_evaluation.dataset_evaluation.iou_averaged_evaluation.ci_evaluations.items():
        _re_arrange_evaluation_element(
            seg_ee=ee, box_ee=box_evaluation.dataset_evaluation.iou_averaged_evaluation.ci_evaluations[ci])
    _re_arrange_evaluation_element(
        seg_ee=seg_evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation,
        box_ee=box_evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation)

    return seg_evaluation
