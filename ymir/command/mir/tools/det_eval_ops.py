import logging
from typing import Dict, Set

from mir.tools import det_eval_coco, det_eval_voc
from mir.protos import mir_command_pb2 as mirpb


def det_evaluate_with_pb(
        predictions: Dict[str, mirpb.SingleTaskAnnotations],
        ground_truth: mirpb.SingleTaskAnnotations,
        config: mirpb.EvaluateConfig,
        mode: str = 'voc',  # voc or coco
) -> mirpb.Evaluation:
    if not config.class_ids:
        config.class_ids.extend(_gen_class_ids_from_gt(ground_truth=ground_truth))

    eval_model_name = det_eval_voc if mode == 'voc' else det_eval_coco
    evaluation = eval_model_name.det_evaluate(  # type: ignore
        predictions=predictions, ground_truth=ground_truth, config=config)

    _show_evaluation(evaluation=evaluation)

    return evaluation


def _gen_class_ids_from_gt(ground_truth: mirpb.SingleTaskAnnotations) -> Set[int]:
    return {
        annotation.class_id
        for image_annotations in ground_truth.image_annotations.values() for annotation in image_annotations.annotations
    }


def _show_evaluation(evaluation: mirpb.Evaluation) -> None:
    if not evaluation.dataset_evaluations:
        logging.info('evaluation result: none')
        return

    gt_dataset_id = evaluation.config.gt_dataset_id
    for dataset_id, dataset_evaluation in evaluation.dataset_evaluations.items():
        cae = dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation
        logging.info(f"evaluation result: gt: {gt_dataset_id}, pred: {dataset_id}, mAP: {cae.ap}")

        for class_id, see in dataset_evaluation.iou_averaged_evaluation.ci_evaluations.items():
            if see.ap > 0:
                logging.info(f"    class id: {class_id}, mAP: {see.ap}")
