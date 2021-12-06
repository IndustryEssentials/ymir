from typing import Dict

from src.libs import app_logger, utils
from src.viz_models import task


def get_task_info(user_id: str, repo_id: str, branch_id: str) -> Dict:
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
    result = task.Task(user_id, repo_id, branch_id).get_model_info()

    resp = utils.suss_resp()
    resp.update({"result": result})
    app_logger.logger.info(f"get_task_info: {resp}")

    return resp
