from typing import List, Optional, Tuple

from mir.tools import det_eval_ops, mir_storage_ops, revs_parser
from mir.protos import mir_command_pb2 as mirpb


def det_evaluate_datasets(
    mir_root: str,
    gt_rev_tid: revs_parser.TypRevTid,
    pred_rev_tid: revs_parser.TypRevTid,
    conf_thr: float,
    iou_thrs: str,
    class_ids: List[int] = [],
    need_pr_curve: bool = False,
    main_ck: str = '',
) -> mirpb.Evaluation:
    mir_annotations: mirpb.MirAnnotations = mir_storage_ops.MirStorageOps.load_single_storage(
        mir_root=mir_root, mir_branch=gt_rev_tid.rev, mir_task_id=gt_rev_tid.tid, ms=mirpb.MirStorage.MIR_ANNOTATIONS)
    ground_truth = mir_annotations.ground_truth

    if pred_rev_tid != gt_rev_tid:
        mir_annotations = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=mir_root,
                                                                            mir_branch=pred_rev_tid.rev,
                                                                            mir_task_id=pred_rev_tid.tid,
                                                                            ms=mirpb.MirStorage.MIR_ANNOTATIONS)
    prediction = mir_annotations.prediction

    evaluate_config = mir_storage_ops.create_evaluate_config(conf_thr=conf_thr,
                                                             iou_thrs=iou_thrs,
                                                             need_pr_curve=need_pr_curve,
                                                             class_ids=class_ids)

    # evaluate
    evaluation = det_eval_ops.det_evaluate_with_pb(
        prediction=prediction,
        ground_truth=ground_truth,
        config=evaluate_config,
    )

    # evaluate with ck
    if main_ck:
        mir_keywords: mirpb.MirKeywords = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=mir_root,
            mir_branch=pred_rev_tid.rev,
            mir_task_id=pred_rev_tid.tid,
            ms=mirpb.MirStorage.MIR_KEYWORDS)
        ck_asset_ids = _sub_ck_and_asset_ids_from_main_ck(mir_keywords=mir_keywords, main_ck=main_ck)

        for sub_ck, asset_ids in ck_asset_ids:
            ck_prediction = _filter_task_annotations_by_asset_ids(task_annotations=prediction, asset_ids=asset_ids)
            ck_ground_truth = _filter_task_annotations_by_asset_ids(task_annotations=ground_truth, asset_ids=asset_ids)
            ck_evaluation = det_eval_ops.det_evaluate_with_pb(
                prediction=ck_prediction,
                ground_truth=ck_ground_truth,
                config=evaluate_config,
            )
            _copy_ck_evaluation_result(evaluation=evaluation,
                                       ck_evaluation=ck_evaluation,
                                       main_ck=main_ck,
                                       sub_ck=sub_ck)

    return evaluation


def _sub_ck_and_asset_ids_from_main_ck(mir_keywords: mirpb.MirKeywords,
                                       main_ck: str) -> List[Tuple[Optional[str], List[str]]]:
    if main_ck not in mir_keywords.ck_idx:
        return []

    ck_idx = mir_keywords.ck_idx[main_ck]

    main_sub_ck_asset_ids: List[Tuple[Optional[str], List[str]]]
    main_sub_ck_asset_ids = [(sub_ck, list(asset_anno_ids.key_ids.keys()))
                             for sub_ck, asset_anno_ids in ck_idx.sub_indexes.items()]
    main_sub_ck_asset_ids.append((None, list(ck_idx.asset_annos.keys())))

    return main_sub_ck_asset_ids


def _filter_task_annotations_by_asset_ids(task_annotations: mirpb.SingleTaskAnnotations,
                                          asset_ids: List[str]) -> mirpb.SingleTaskAnnotations:
    filtered_task_annotations = mirpb.SingleTaskAnnotations()
    for asset_id in asset_ids:
        if asset_id not in task_annotations.image_annotations:
            continue
        filtered_task_annotations.image_annotations[asset_id].CopyFrom(task_annotations.image_annotations[asset_id])
    return filtered_task_annotations


def _copy_ck_evaluation_result(evaluation: mirpb.Evaluation,
                               ck_evaluation: mirpb.Evaluation,
                               main_ck: str,
                               sub_ck: Optional[str] = None) -> None:
    if sub_ck is None:
        for iou_thr_str, ck_iou_evaluation in ck_evaluation.dataset_evaluation.iou_evaluations.items():
            evaluation.dataset_evaluation.iou_evaluations[iou_thr_str].ck_evaluations[main_ck].total.CopyFrom(
                ck_iou_evaluation.ci_averaged_evaluation)
        evaluation.dataset_evaluation.iou_averaged_evaluation.ck_evaluations[main_ck].total.CopyFrom(
            ck_evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation)
    else:
        for iou_thr_str, ck_iou_evaluation in ck_evaluation.dataset_evaluation.iou_evaluations.items():
            evaluation.dataset_evaluation.iou_evaluations[iou_thr_str].ck_evaluations[main_ck].sub[sub_ck].CopyFrom(
                ck_iou_evaluation.ci_averaged_evaluation)
        evaluation.dataset_evaluation.iou_averaged_evaluation.ck_evaluations[main_ck].sub[sub_ck].CopyFrom(
            ck_evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation)
