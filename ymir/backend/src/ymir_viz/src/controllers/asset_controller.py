from typing import Dict

from src.libs import app_logger, utils
from src.viz_models import asset


# Return type: AssetMetaResult
def get_assert_id_info(user_id: str, repo_id: str, branch_id: str, asset_id: str) -> Dict:
    result = asset.AssetsModel(user_id, repo_id, branch_id).get_asset_id_info(asset_id)

    resp = utils.suss_resp(result=result)
    app_logger.logger.info(f"get_assert_id_info: {resp}")

    return resp


# Return type: AssetMetaResult
def get_asserts_info(
    user_id: str, repo_id: str, branch_id: str, offset: int = 0, limit: int = 20, class_id: int = None,
) -> Dict:
    """
    API get assetst info
    """
    result = asset.AssetsModel(user_id, repo_id, branch_id).get_assets_info(offset, limit, class_id)

    resp = utils.suss_resp(result=result)
    app_logger.logger.info(f"get_asserts_info: {resp}")

    return resp
