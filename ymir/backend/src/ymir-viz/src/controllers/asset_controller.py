from typing import Dict

from src.libs import app_logger, utils
from src.viz_models import asset


def get_assert_id_info(user_id: str, repo_id: str, branch_id: str, asset_id: str) -> Dict:
    result = asset.Asset(user_id, repo_id, branch_id).get_asset_id_info(asset_id)

    resp = utils.suss_resp()
    resp.update({"result": result})
    app_logger.logger.info(f"get_assert_id_info: {resp}")

    return resp


def get_asserts_info(
    user_id: str, repo_id: str, branch_id: str, offset: int = 0, limit: int = 20, class_id: int = None,
) -> Dict:
    """
    API get assetst info
    """
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    result = asset.Asset(user_id, repo_id, branch_id).get_assets_info(offset, limit, class_id)

    resp = utils.suss_resp()
    resp.update({"result": result})
    app_logger.logger.error(f"get_asserts_info: {resp}")

    return resp
