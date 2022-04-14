import logging

from src.config import viz_settings
from src.libs import utils
from src.swagger_models.dataset_result import DatasetResult
from src.viz_models import pb_reader


def get_dataset_info(user_id: str, repo_id: str, branch_id: str) -> DatasetResult:
    """get dataset info

    get dataset info # noqa: E501

    :param user_id: user_id
    :type user_id: str
    :param repo_id: repo_id
    :type repo_id: str
    :param branch_id: branch_id
    :type branch_id: str

    :rtype: DatasetResult

    exampled return data:
    {
        "class_ids_count": {3: 34},
        "class_names_count": {'cat': 34},
        "ignored_labels": {'cat':5, },
        "negative_info": {
            "negative_images_cnt": 0,
            "project_negative_images_cnt": 0,
        },
        "total_images_cnt": 1,
    }
    """
    dataset_info = pb_reader.MirStorageLoader(
        sandbox_root=viz_settings.BACKEND_SANDBOX_ROOT,
        user_id=user_id,
        repo_id=repo_id,
        branch_id=branch_id,
        task_id=branch_id,
    ).get_dataset_info()

    resp = utils.suss_resp(result=dataset_info)
    logging.info(f"get_dataset_info: {resp}")

    return DatasetResult(**resp)
