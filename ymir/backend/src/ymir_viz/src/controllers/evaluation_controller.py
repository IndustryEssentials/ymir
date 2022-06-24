import logging
import os

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import det_eval as mir_det_eval, mir_storage_ops, revs_parser

from src.config import viz_settings
from src.libs import utils
from src.swagger_models import DatasetEvaluationResult
from src.viz_models import pb_reader


def get_dataset_evaluations(user_id: str, repo_id: str, branch_id: str) -> DatasetEvaluationResult:
    """
    get dataset evaluations result

    :param user_id: user_id
    :type user_id: str
    :param repo_id: repo_id
    :type repo_id: str
    :param branch_id: branch_id
    :type branch_id: str

    :rtype: DatasetEvaluationResult
    """
    evaluations = pb_reader.MirStorageLoader(
        sandbox_root=viz_settings.BACKEND_SANDBOX_ROOT,
        user_id=user_id,
        repo_id=repo_id,
        branch_id=branch_id,
        task_id=branch_id,
    ).get_dataset_evaluations()

    resp = utils.suss_resp()
    resp["result"] = evaluations
    logging.info("successfully get_dataset_evaluations from branch %s", branch_id)

    return DatasetEvaluationResult(**resp)


def dataset_fast_evaluation(user_id: str, repo_id: str, branch_id: str, conf_thr: float,
                            iou_thr: float) -> DatasetEvaluationResult:
    # rev_tid = revs_parser.parse_single_arg_rev(branch_id)
    # mir_root = os.path.join(viz_settings.BACKEND_SANDBOX_ROOT, user_id, repo_id)

    # mir_metadatas: mirpb.MirMetadatas
    # mir_annotations: mirpb.MirAnnotations
    # mir_keywords: mirpb.MirKeywords
    # mir_metadatas, mir_annotations, mir_keywords = mir_storage_ops.MirStorageOps.load_multiple_storages(
    #     mir_root=mir_root,
    #     mir_branch=rev_tid.rev,
    #     mir_task_id=rev_tid.tid,
    #     ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS])

    # pred_task_annotations = mir_annotations.task_annotations[mir_annotations.head_task_id]
    # gt_task_annotations = mir_annotations.ground_truth

    # mir_gt = mir_det_eval.MirCoco(mir_metadatas=mir_metadatas,
    #                               task_annotations=gt_task_annotations,
    #                               mir_keywords=mir_keywords,
    #                               conf_thr=conf_thr)
    # mir_dt = mir_det_eval.MirCoco(mir_metadatas=mir_metadatas,
    #                               task_annotations=pred_task_annotations,
    #                               mir_keywords=mir_keywords,
    #                               conf_thr=conf_thr)
    # evaluator = mir_det_eval.MirDetEval(coco_gt=mir_gt, coco_dt=mir_dt)
    return DatasetEvaluationResult()
