from typing import List

from app.utils.cache import CacheClient
from app.utils.ymir_controller import ControllerClient
from common_utils.labels import SingleLabel, UserLabels


def add_keywords(controller: ControllerClient, cache: CacheClient, user_id: int, keywords: List[str]) -> None:
    controller.add_labels(
        user_id,
        UserLabels(labels=[SingleLabel(name=k) for k in keywords]),
        dry_run=False,
    )
    cache.delete_personal_keywords_cache()
