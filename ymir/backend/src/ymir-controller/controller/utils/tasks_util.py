import logging
from datetime import datetime
from typing import List

import requests

from common_utils.percent_log_util import LogState
from controller.config import common_task as common_task_config
from controller.utils import errors
from id_definition.error_codes import CTLResponseCode


def write_task_progress(monitor_file: str,
                        tid: str,
                        percent: float,
                        state: LogState,
                        error_code: int = None,
                        error_message: str = None,
                        msg: str = None) -> CTLResponseCode:
    if not monitor_file:
        raise RuntimeError("Invalid monitor_file")
    content_list: List[str] = [tid, str(int(datetime.now().timestamp())), str(percent), str(state.value)]
    if error_code and error_message:
        content_list.extend([str(error_code), error_message])
    content = '\t'.join(content_list)
    if msg:
        content = '\n'.join([content, msg])
    with open(monitor_file, 'w') as f:
        logging.info(f"writing task info to {monitor_file}\n{content}")
        f.write(content)
    return CTLResponseCode.CTR_OK


def register_monitor_log(task_id: str, user_id: str, log_paths: List[str], description: str = None) -> None:
    resp = requests.post(
        url=f"{common_task_config.MONITOR_URL}/api/v1/tasks",
        json=dict(task_id=task_id, user_id=user_id, log_paths=log_paths, description=description),
        timeout=5,
    )

    if resp.status_code != 200:
        raise errors.MirCtrError(CTLResponseCode.REG_LOG_MONITOR_ERROR, f"reg to monitor service error: {resp.content}")
