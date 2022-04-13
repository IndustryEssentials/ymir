import logging

from src.config import viz_settings
from src.libs import utils
from src.swagger_models.model_result import ModelResult
from src.viz_models import pb_reader


def get_model_info(user_id: str, repo_id: str, branch_id: str) -> ModelResult:
    """
    get task model info

    :param user_id: user_id
    :type user_id: str
    :param repo_id: repo_id
    :type repo_id: str
    :param branch_id: branch_id
    :type branch_id: str

    :rtype: ModelResult
    """
    model_info = pb_reader.MirStorageLoader(
        sandbox_root=viz_settings.BACKEND_SANDBOX_ROOT,
        user_id=user_id,
        repo_id=repo_id,
        branch_id=branch_id,
        task_id=branch_id,
    ).get_model_info()

    resp = utils.suss_resp()
    resp.update({
        "result":
        dict(
            model_id=model_info["model_hash"],
            model_mAP=model_info["mean_average_precision"],
            task_parameters=model_info["task_parameters"],
            executor_config=model_info["executor_config"],
        )
    })
    logging.info(f"get_model_info: {resp}")

    return ModelResult(**resp)
