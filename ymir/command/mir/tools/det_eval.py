import logging
from typing import List, Tuple

from mir.tools import mir_storage_ops, revs_parser, det_eval_coco, det_eval_voc
from mir.tools.det_eval_dataset import MirDataset
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
    for dataset_evaluation in evaluation.dataset_evaluations.values():
        _calc_averaged_evaluations(dataset_evaluation=dataset_evaluation, class_ids=mir_dt.get_class_ids())

    _show_evaluation(evaluation=evaluation)

    return (evaluation, mir_annotations)


def _calc_averaged_evaluations(dataset_evaluation: mirpb.SingleDatasetEvaluation, class_ids: List[int]) -> None:
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

    for ee in ees:
        average_ee.ap += ee.ap
        average_ee.ar += ee.ar
        average_ee.tp += ee.tp
        average_ee.fp += ee.fp
        average_ee.fn += ee.fn

    ees_cnt = len(ees)
    average_ee.ap /= ees_cnt
    average_ee.ar /= ees_cnt


def _show_evaluation(evaluation: mirpb.Evaluation) -> None:
    if not evaluation.dataset_evaluations:
        logging.info('evaluation result: none')
        return

    gt_dataset_id = evaluation.config.gt_dataset_id
    for dataset_id, dataset_evaluation in evaluation.dataset_evaluations.items():
        cae = dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation
        logging.info(f"evaluation result: gt: {gt_dataset_id}, pred: {dataset_id}, mAP: {cae.ap}")
