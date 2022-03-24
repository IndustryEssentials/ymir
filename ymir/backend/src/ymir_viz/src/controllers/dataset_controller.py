from typing import Dict

from src.config import viz_settings
from src.libs import app_logger, utils
from src.viz_models import pb_reader


def get_dataset_info(user_id: str, repo_id: str, branch_id: str) -> Dict:
    """get dataset info

    get dataset info # noqa: E501

    :param user_id: user_id
    :type user_id: str
    :param repo_id: repo_id
    :type repo_id: str
    :param branch_id: branch_id
    :type branch_id: str

    :rtype: DatasetResult
    """
    dataset_info = pb_reader.MirStorageLoader(
        sandbox_root=viz_settings.VIZ_SANDBOX_ROOT,
        user_id=user_id,
        repo_id=repo_id,
        branch_id=branch_id,
        task_id=branch_id,
    ).get_dataset_info()

    resp = utils.suss_resp(result=dataset_info)
    app_logger.logger.info(f"get_dataset_info: {resp}")

    return resp
