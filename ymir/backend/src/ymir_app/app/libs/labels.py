from typing import Dict

from fastapi.logger import logger

from app.utils.ymir_controller import ControllerClient
from common_utils.labels import UserLabels


def upsert_labels(
    user_id: int,
    user_labels: UserLabels,
    new_user_labels: UserLabels,
    controller_client: ControllerClient,
    dry_run: bool = False,
) -> Dict:
    """
    update or insert labels
    """
    logger.info(f"old labels: {user_labels.json()}\nnew labels: {new_user_labels.json()}")
    resp = controller_client.add_labels(user_id, new_user_labels, dry_run)

    conflict_labels = []
    if resp.get("label_collection"):
        for conflict_label in resp["label_collection"]["labels"]:
            conflict_labels += [conflict_label["name"]] + conflict_label["aliases"]

    return {"failed": conflict_labels}
