from functools import partial
from typing import Collection, Optional

from mir.tools import mir_storage_ops, revs_parser, settings as mir_settings
from mir.tools.eval import eval_ops
from mir.protos import mir_command_pb2 as mirpb


def evaluate_datasets(
    mir_root: str,
    gt_rev_tid: revs_parser.TypRevTid,
    pred_rev_tid: revs_parser.TypRevTid,
    evaluate_config: mirpb.EvaluateConfig,
) -> Optional[mirpb.Evaluation]:
    gt_mir_annotations: mirpb.MirAnnotations = mir_storage_ops.MirStorageOps.load_single_storage(
        mir_root=mir_root, mir_branch=gt_rev_tid.rev, mir_task_id=gt_rev_tid.tid, ms=mirpb.MirStorage.MIR_ANNOTATIONS)
    ground_truth = gt_mir_annotations.ground_truth
    if ground_truth.type == mirpb.ObjectType.OT_SEG:
        assets_metadata = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=mir_root,
                                                                            mir_branch=gt_rev_tid.rev,
                                                                            mir_task_id=gt_rev_tid.tid,
                                                                            ms=mirpb.MirStorage.MIR_METADATAS)
    else:
        assets_metadata = None

    if pred_rev_tid != gt_rev_tid:
        pred_mir_annotations = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=mir_root,
                                                                                 mir_branch=pred_rev_tid.rev,
                                                                                 mir_task_id=pred_rev_tid.tid,
                                                                                 ms=mirpb.MirStorage.MIR_ANNOTATIONS)
    else:
        pred_mir_annotations = gt_mir_annotations
    prediction = pred_mir_annotations.prediction

    # evaluate
    evaluation = eval_ops.evaluate_with_pb(
        prediction=prediction,
        ground_truth=ground_truth,
        config=evaluate_config,
        assets_metadata=assets_metadata,
    )
    if evaluation.state != mirpb.EvaluationState.ES_READY:
        return None

    # evaluate with ck
    if evaluate_config.main_ck:
        mir_keywords: mirpb.MirKeywords = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=mir_root,
            mir_branch=pred_rev_tid.rev,
            mir_task_id=pred_rev_tid.tid,
            ms=mirpb.MirStorage.MIR_KEYWORDS)

        if evaluate_config.main_ck not in mir_keywords.ck_idx:
            return None

        ck_evaluate_config = mirpb.EvaluateConfig()
        ck_evaluate_config.CopyFrom(evaluate_config)
        ck_evaluate_config.need_pr_curve = False
        ck_idx = mir_keywords.ck_idx[ck_evaluate_config.main_ck]
        ck_evaluate_func = partial(_evaluate_on_asset_ids, ground_truth, prediction, ck_evaluate_config)

        # fill main ck.
        ck_evaluate_func(ck_idx.asset_annos, evaluation.main_ck)
        # fill sub ck.
        for idx, (sub_ck, asset_anno_ids) in enumerate(ck_idx.sub_indexes.items()):
            if idx >= mir_settings.DEFAULT_EVALUATE_SUB_CKS:
                break
            ck_evaluate_func(asset_anno_ids.key_ids, evaluation.sub_cks[sub_ck])

    return evaluation


def _evaluate_on_asset_ids(gt: mirpb.SingleTaskAnnotations, pred: mirpb.SingleTaskAnnotations,
                           evaluate_config: mirpb.EvaluateConfig, asset_ids: Collection[str],
                           target: mirpb.SingleDatasetEvaluation) -> None:
    pred = _filter_task_annotations_by_asset_ids(task_annotations=pred, asset_ids=asset_ids)
    gt = _filter_task_annotations_by_asset_ids(task_annotations=gt, asset_ids=asset_ids)
    evaluation = eval_ops.evaluate_with_pb(
        prediction=pred,
        ground_truth=gt,
        config=evaluate_config,
    )
    if evaluation.state == mirpb.EvaluationState.ES_READY:
        target.CopyFrom(evaluation.dataset_evaluation)


def _filter_task_annotations_by_asset_ids(task_annotations: mirpb.SingleTaskAnnotations,
                                          asset_ids: Collection[str]) -> mirpb.SingleTaskAnnotations:
    filtered_task_annotations = mirpb.SingleTaskAnnotations()
    filtered_task_annotations.type = task_annotations.type
    filtered_task_annotations.is_instance_segmentation = task_annotations.is_instance_segmentation
    for asset_id in asset_ids:
        if asset_id not in task_annotations.image_annotations:
            continue
        filtered_task_annotations.image_annotations[asset_id].CopyFrom(task_annotations.image_annotations[asset_id])
    return filtered_task_annotations
