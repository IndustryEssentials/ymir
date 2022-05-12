import logging

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
