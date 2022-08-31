from typing import List

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

    return det_eval_ops.det_evaluate_with_pb(
        prediction=prediction,
        ground_truth=ground_truth,
        config=evaluate_config,
    )
