import logging
import time
from types import ModuleType
from typing import Any, Optional

from mir.tools import det_eval_coco, det_eval_voc, settings as mir_settings
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


def det_evaluate_with_pb(
    prediction: mirpb.SingleTaskAnnotations,
    ground_truth: mirpb.SingleTaskAnnotations,
    config: mirpb.EvaluateConfig,
    assets_metadata: Optional[mirpb.MirMetadatas] = None,
) -> mirpb.Evaluation:
    if config.conf_thr < 0 or config.conf_thr > 1:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="invalid conf_thr")

    if config.type and not (config.type == prediction.type == ground_truth.type):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message="inconsistent evaluate_config object_type")

    if not config.class_ids:
        config.class_ids.extend(prediction.eval_class_ids)

    evaluation = mirpb.Evaluation()
    evaluation.config.CopyFrom(config)
    if not config.class_ids:
        logging.warning("skip evaluation: no evaluate class ids")
        evaluation.state = mirpb.EvaluationState.ES_NO_CLASS_IDS
        return evaluation
    gt_cnt = len(ground_truth.image_annotations)
    pred_cnt = len(prediction.image_annotations)
    if gt_cnt == 0 or pred_cnt == 0:
        logging.warning("skip evaluation: no gt or pred")
        evaluation.state = mirpb.EvaluationState.ES_NO_GT_OR_PRED
        return evaluation
    if (
        len(config.class_ids) > mir_settings.MAX_EVALUATION_CLASS_IDS_COUNT
        or max(gt_cnt, pred_cnt) > mir_settings.MAX_EVALUATION_ASSETS_COUNT
    ):
        logging.warning(
            f"skip evaluation: too many class ids, gt or pred, cis: {len(config.class_ids)}, "
            f"pred: {pred_cnt}, gt: {gt_cnt}"
        )
        evaluation.state = mirpb.EvaluationState.ES_EXCEEDS_LIMIT
        return evaluation

    f_eval_model = _get_eval_model_function(prediction.type)
    if not f_eval_model:
        logging.warning(f"skip evaluation: anno type: {prediction.type} not supported")
        evaluation.state = mirpb.EvaluationState.ES_NOT_SET
        return evaluation

    start_time = time.time()
    for image_annotations in prediction.image_annotations.values():
        for annotation in image_annotations.boxes:
            annotation.cm = mirpb.ConfusionMatrixType.IGNORED
            annotation.det_link_id = -1
    for image_annotations in ground_truth.image_annotations.values():
        for annotation in image_annotations.boxes:
            annotation.cm = mirpb.ConfusionMatrixType.IGNORED
            annotation.det_link_id = -1
    evaluation = f_eval_model.det_evaluate(  # type: ignore
        prediction=prediction, ground_truth=ground_truth, config=config, assets_metadata=assets_metadata
    )

    logging.info(f"|-det_evaluate_with_pb-eval costs {(time.time() - start_time):.2f}s.")

    _show_evaluation(evaluation=evaluation)

    return evaluation


def _get_eval_model_function(anno_type: Any) -> Optional[ModuleType]:
    mapping = {
        mirpb.ObjectType.OT_DET_BOX: det_eval_voc,
        mirpb.ObjectType.OT_SEG: det_eval_coco,
    }
    return mapping.get(anno_type)


def _show_evaluation(evaluation: mirpb.Evaluation) -> None:
    ciae = evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation
    logging.info(f"evaluation result: mAP: {ciae.ap}")

    for class_id, see in evaluation.dataset_evaluation.iou_averaged_evaluation.ci_evaluations.items():
        if see.ap > 0:
            logging.info(f"    class id: {class_id}, mAP: {see.ap}")
