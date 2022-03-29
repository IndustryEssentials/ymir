import logging

from src.libs import utils
from src.swagger_models.asset_meta_result import AssetMetaResult
from src.viz_models import asset


# Return type: AssetMetaResult
def get_assert_id_info(user_id: str, repo_id: str, branch_id: str, asset_id: str) -> AssetMetaResult:
    result = asset.AssetsModel(user_id, repo_id, branch_id).get_asset_id_info(asset_id)

    resp = utils.suss_resp(result=result)
    logging.info(f"get_assert_id_info: {resp}")

    return AssetMetaResult(**resp)


# Return type: AssetMetaResult
def get_asserts_info(
    user_id: str,
    repo_id: str,
    branch_id: str,
    offset: int = 0,
    limit: int = 20,
    class_id: int = None,
) -> AssetMetaResult:
    """
    API get assetst info
    """
    result = asset.AssetsModel(user_id, repo_id, branch_id).get_assets_info(offset, limit, class_id)

    resp = utils.suss_resp(result=result)
    logging.info(f"get_asserts_info: {resp}")

    return AssetMetaResult(**resp)
