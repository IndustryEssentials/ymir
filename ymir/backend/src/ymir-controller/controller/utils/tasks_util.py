from typing import Dict

import requests

from controller.config import common_task as common_task_config
from controller.utils import errors
from id_definition.error_codes import CTLResponseCode


def register_monitor_log(
    task_id: str,
    user_id: str,
    log_paths_weights: Dict[str, float],
    description: str = None,
) -> None:
    resp = requests.post(
        url=f"{common_task_config.MONITOR_URL}/api/v1/tasks",
        json=dict(
            task_id=task_id,
            user_id=user_id,
            log_paths_weights=log_paths_weights,
            description=description,
        ),
        timeout=5,
    )

    if resp.status_code != 200:
        raise errors.MirCtrError(
            CTLResponseCode.REG_LOG_MONITOR_ERROR,
            f"reg to monitor service error: {resp.text}",
        )
