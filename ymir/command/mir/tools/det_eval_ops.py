import logging
from typing import Set

from mir.tools import det_eval_coco, det_eval_voc, det_eval_utils
from mir.protos import mir_command_pb2 as mirpb


def det_evaluate_with_pb(
        prediction: mirpb.SingleTaskAnnotations,
        ground_truth: mirpb.SingleTaskAnnotations,
        config: mirpb.EvaluateConfig,
        mode: str = 'voc',  # voc or coco
) -> mirpb.Evaluation:
    if not config.class_ids:
        config.class_ids.extend(_gen_class_ids_from_gt(ground_truth=ground_truth))

    det_eval_utils.reset_default_confusion_matrix(task_annotations=prediction,
                                                  cm=mirpb.ConfusionMatrixType.NotSet)
    det_eval_utils.reset_default_confusion_matrix(task_annotations=ground_truth,
                                                  cm=mirpb.ConfusionMatrixType.NotSet)

    eval_model_name = det_eval_voc if mode == 'voc' else det_eval_coco
    evaluation = eval_model_name.det_evaluate(  # type: ignore
        prediction=prediction, ground_truth=ground_truth, config=config)

    _show_evaluation(evaluation=evaluation)

    return evaluation


def _gen_class_ids_from_gt(ground_truth: mirpb.SingleTaskAnnotations) -> Set[int]:
    return {
        annotation.class_id
        for image_annotations in ground_truth.image_annotations.values() for annotation in image_annotations.annotations
    }


def _show_evaluation(evaluation: mirpb.Evaluation) -> None:
    ciae = evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation
    logging.info(f"evaluation result: mAP: {ciae.ap}")

    for class_id, see in evaluation.dataset_evaluation.iou_averaged_evaluation.ci_evaluations.items():
        if see.ap > 0:
            logging.info(f"    class id: {class_id}, mAP: {see.ap}")
