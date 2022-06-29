import logging
import os

from google.protobuf import json_format
from mir.tools import det_eval, revs_parser

from src.config import viz_settings
from src.libs import utils
from src.libs import exceptions
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


@exceptions.catch_exceptions
def dataset_fast_evaluation(user_id: str, repo_id: str, branch_id: str, conf_thr: float, iou_thr: float,
                            need_pr_curve: bool) -> DatasetEvaluationResult:
    rev_tid = revs_parser.parse_single_arg_rev(branch_id, need_tid=False)
    mir_root = os.path.join(viz_settings.BACKEND_SANDBOX_ROOT, user_id, repo_id)

    evaluation = det_eval.det_evaluate(mir_root=mir_root,
                                       rev_tid=rev_tid,
                                       conf_thr=conf_thr,
                                       iou_thrs=str(iou_thr),
                                       need_pr_curve=need_pr_curve)

    logging.info(f"successfully dataset_fast_evaluation from branch {branch_id}")

    resp = utils.suss_resp()
    resp["result"] = json_format.MessageToDict(evaluation,
                                               including_default_value_fields=True,
                                               preserving_proto_field_name=True,
                                               use_integers_for_enums=True)['dataset_evaluations']
    return DatasetEvaluationResult(**resp)
