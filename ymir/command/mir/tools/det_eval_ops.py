import logging
from typing import List

from mir.tools import mir_storage_ops, revs_parser, det_eval_coco, det_eval_voc
from mir.protos import mir_command_pb2 as mirpb


def det_evaluate(
    mir_root: str,
    gt_rev_tid: revs_parser.TypRevTid,
    pred_rev_tid: revs_parser.TypRevTid,
    conf_thr: float,
    iou_thrs: str,
    class_ids: List[int] = [],
    need_pr_curve: bool = False,
) -> mirpb.Evaluation:
    mir_annotations: mirpb.MirAnnotations
    mir_keywords: mirpb.MirKeywords
    mir_annotations, mir_keywords = mir_storage_ops.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=gt_rev_tid.rev,
        mir_task_id=gt_rev_tid.tid,
        ms_list=[mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS])
    ground_truth = mir_annotations.ground_truth

    if pred_rev_tid != gt_rev_tid:
        mir_annotations = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=mir_root,
                                                                            mir_branch=pred_rev_tid.rev,
                                                                            mir_task_id=pred_rev_tid.tid,
                                                                            ms=mirpb.MirStorage.MIR_ANNOTATIONS)
    prediction = mir_annotations.prediction

    return det_evaluate_with_pb(
        prediction=prediction,
        ground_truth=ground_truth,
        gt_dataset_id=gt_rev_tid.rev_tid,
        pred_dataset_id=pred_rev_tid.rev_tid,
        conf_thr=conf_thr,
        iou_thrs=iou_thrs,
        class_ids=class_ids or list(mir_keywords.gt_idx.cis.keys()),
        need_pr_curve=need_pr_curve,
    )


def det_evaluate_with_pb(
        prediction: mirpb.SingleTaskAnnotations,
        ground_truth: mirpb.SingleTaskAnnotations,
        gt_dataset_id: str,
        pred_dataset_id: str,
        conf_thr: float,
        iou_thrs: str,
        class_ids: List[int] = [],
        need_pr_curve: bool = False,
        mode: str = 'voc',  # voc or coco
) -> mirpb.Evaluation:
    # evaluation = mirpb.Evaluation()
    evaluate_config = mirpb.EvaluateConfig()
    evaluate_config.conf_thr = conf_thr
    evaluate_config.iou_thrs_interval = iou_thrs
    evaluate_config.need_pr_curve = need_pr_curve
    evaluate_config.gt_dataset_id = gt_dataset_id
    evaluate_config.pred_dataset_ids.append(pred_dataset_id)
    evaluate_config.class_ids[:] = class_ids

    eval_model_name = det_eval_voc if mode == 'voc' else det_eval_coco
    evaluation = eval_model_name.det_evaluate(  # type: ignore
        predictions=[prediction],
        ground_truth=ground_truth,
        config=evaluate_config)

    _show_evaluation(evaluation=evaluation)

    return evaluation


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
