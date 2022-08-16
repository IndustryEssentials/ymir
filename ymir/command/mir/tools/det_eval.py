import logging
from typing import Tuple

from mir.tools import mir_storage_ops, revs_parser, det_eval_coco, det_eval_voc
from mir.tools.det_eval_utils import MirDataset
from mir.protos import mir_command_pb2 as mirpb


def det_evaluate(
    mir_root: str,
    rev_tid: revs_parser.TypRevTid,
    conf_thr: float,
    iou_thrs: str,
    need_pr_curve: bool = False,
) -> Tuple[mirpb.Evaluation, mirpb.MirAnnotations]:
    mir_metadatas: mirpb.MirMetadatas
    mir_annotations: mirpb.MirAnnotations
    mir_keywords: mirpb.MirKeywords
    mir_metadatas, mir_annotations, mir_keywords = mir_storage_ops.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=rev_tid.rev,
        mir_task_id=rev_tid.tid,
        ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS])

    return det_evaluate_with_pb(
        mir_metadatas=mir_metadatas,
        mir_annotations=mir_annotations,
        mir_keywords=mir_keywords,
        dataset_id=rev_tid.rev_tid,
        conf_thr=conf_thr,
        iou_thrs=iou_thrs,
        need_pr_curve=need_pr_curve,
    )


def det_evaluate_with_pb(
    mir_metadatas: mirpb.MirMetadatas,
    mir_annotations: mirpb.MirAnnotations,
    mir_keywords: mirpb.MirKeywords,
    dataset_id: str,
    conf_thr: float,
    iou_thrs: str,
    need_pr_curve: bool = False,
) -> Tuple[mirpb.Evaluation, mirpb.MirAnnotations]:
    mir_gt = MirDataset(mir_metadatas=mir_metadatas,
                        mir_annotations=mir_annotations,
                        mir_keywords=mir_keywords,
                        conf_thr=conf_thr,
                        dataset_id=dataset_id,
                        as_gt=True)
    mir_dt = MirDataset(mir_metadatas=mir_metadatas,
                        mir_annotations=mir_annotations,
                        mir_keywords=mir_keywords,
                        conf_thr=conf_thr,
                        dataset_id=dataset_id,
                        as_gt=False)

    # evaluation = mirpb.Evaluation()
    evaluate_config = mirpb.EvaluateConfig()
    evaluate_config.conf_thr = conf_thr
    evaluate_config.iou_thrs_interval = iou_thrs
    evaluate_config.need_pr_curve = need_pr_curve
    evaluate_config.gt_dataset_id = dataset_id
    evaluate_config.pred_dataset_ids.append(dataset_id)

    evaluation = det_eval_voc.det_evaluate(mir_dts=[mir_dt], mir_gt=mir_gt, config=evaluate_config)

    _show_evaluation(evaluation=evaluation)

    return (evaluation, mir_annotations)


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
