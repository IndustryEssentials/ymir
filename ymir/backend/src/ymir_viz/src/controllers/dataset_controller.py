import logging

from src.config import viz_settings
from src.libs import utils, exceptions
from src.swagger_models.dataset_result import DatasetResult
from src.swagger_models.dataset_duplication_result import DatasetDuplicationResult
from src.viz_models import asset, pb_reader


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


def check_datasets_duplication(
    user_id: str,
    repo_id: str,
    candidate_dataset_ids: str,
) -> DatasetDuplicationResult:
    dataset_ids = [dataset_id.strip() for dataset_id in candidate_dataset_ids.split(",")]
    try:
        main_dataset_id, other_dataset_id = dataset_ids
    except ValueError:
        logging.exception("invalid candidate_dataset_ids. only two dataset_ids for now")
        raise exceptions.TooManyDatasetsToCheck()

    # fixme: find efficient way to check duplication
    main_asset_ids = asset.AssetsModel(user_id, repo_id, main_dataset_id).get_all_asset_ids()
    other_asset_ids = asset.AssetsModel(user_id, repo_id, other_dataset_id).get_all_asset_ids()

    duplication_count = len(set(main_asset_ids).intersection(other_asset_ids))
    resp = utils.suss_resp(result=duplication_count)
    return DatasetDuplicationResult(**resp)


def get_dataset_stats(
    user_id: str,
    repo_id: str,
    branch_id: str,
    class_ids: str,
) -> DatasetResult:
    """get dataset stats info

    Args:
        user_id (str): user id
        repo_id (str): repo id
        branch_id (str): dataset hash
        class_ids (List[int]): class ids

    Returns: DatasetResult

    return example:
    {
        "class_ids_count": {3: 34},
        "negative_info": {
            "negative_images_cnt": 6,
        },
        "total_images_cnt": 40,
    }
    """
    pass
