from typing import Dict, List, Tuple

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
    main_ck: bool = '',
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
        main_asset_ids, sub_ck_to_asset_ids = _asset_ids_from_main_ck(mir_keywords=mir_keywords, main_ck=main_ck)

        # evaluate with main ck
        main_ck_prediction = _filter_task_annotations_by_asset_ids(task_annotations=prediction,
                                                                   asset_ids=main_asset_ids)
        main_ck_ground_truth = _filter_task_annotations_by_asset_ids(task_annotations=ground_truth,
                                                                     asset_ids=main_asset_ids)
        main_ck_evaluation = det_eval_ops.det_evaluate_with_pb(
            prediction=main_ck_prediction,
            ground_truth=main_ck_ground_truth,
            config=evaluate_config,
        )

        # evaluate with sub cks
        for sub_ck, sub_asset_ids in sub_ck_to_asset_ids.items():
            sub_ck_prediction = _filter_task_annotations_by_asset_ids(task_annotations=prediction,
                                                                      asset_ids=sub_asset_ids)
            sub_ck_ground_truth = _filter_task_annotations_by_asset_ids(task_annotations=ground_truth,
                                                                        asset_ids=sub_asset_ids)
            sub_ck_evaluation = det_eval_ops.det_evaluate_with_pb(
                prediction=sub_ck_prediction,
                ground_truth=sub_ck_ground_truth,
                config=evaluate_config,
            )
    return evaluation


def _asset_ids_from_main_ck(mir_keywords: mirpb.MirKeywords, main_ck: str) -> Tuple[List[str], Dict[str, List[str]]]:
    if main_ck not in mir_keywords.ck_idx:
        return ([], {})

    ck_idx = mir_keywords.ck_idx[main_ck]
    main_asset_ids = list(ck_idx.asset_annos.keys())
    sub_asset_ids = {
        sub_ck: list(asset_anno_ids.key_ids.keys())
        for sub_ck, asset_anno_ids in ck_idx.sub_indexes.items()
    }

    return (main_asset_ids, sub_asset_ids)


def _filter_task_annotations_by_asset_ids(task_annotations: mirpb.SingleTaskAnnotations,
                                          asset_ids: List[str]) -> mirpb.SingleTaskAnnotations:
    filtered_task_annotations = mirpb.SingleTaskAnnotations()
    for asset_id in asset_ids:
        if asset_id not in task_annotations.image_annotations:
            continue
        filtered_task_annotations.image_annotations[asset_id].CopyFrom(task_annotations.image_annotations[asset_id])
    return filtered_task_annotations
