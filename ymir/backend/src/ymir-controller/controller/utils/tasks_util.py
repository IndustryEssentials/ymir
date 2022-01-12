from datetime import datetime
from typing import List

import requests

from controller.config import common_task as common_task_config
from controller.utils import code
from controller.utils.app_logger import logger
from proto import backend_pb2


def task_state_str_to_code(state: str) -> backend_pb2.TaskState:
    _task_state_to_enum = {
        "pending": backend_pb2.TaskState.TaskStatePending,
        "running": backend_pb2.TaskState.TaskStateRunning,
        "runing": backend_pb2.TaskState.TaskStateRunning,
        "done": backend_pb2.TaskState.TaskStateDone,
        "error": backend_pb2.TaskState.TaskStateError,
    }
    return _task_state_to_enum[state]


def task_state_code_to_str(state: backend_pb2.TaskState) -> str:
    _dict_enum_to_str = {
        backend_pb2.TaskState.TaskStatePending: "pending",
        backend_pb2.TaskState.TaskStateRunning: "running",
        backend_pb2.TaskState.TaskStateDone: "done",
        backend_pb2.TaskState.TaskStateError: "error",
    }
    return _dict_enum_to_str[state]


def write_task_progress(monitor_file: str,
                        tid: str,
                        percent: float,
                        state: backend_pb2.TaskState,
                        msg: str = None) -> code.ResCode:
    if not monitor_file:
        raise RuntimeError("Invalid monitor_file")
    with open(monitor_file, 'w') as f:
        f.write('\t'.join([tid, str(int(datetime.now().timestamp())), str(percent), task_state_code_to_str(state)]))
        if msg:
            f.write('\n{}'.format(msg))
    return code.ResCode.CTR_OK


def register_monitor_log(task_id: str, user_id: str, log_path: List[str], description: str = None) -> None:
    # compatible with old modes, remove the try when ready
    try:

        requests.post(
            url=f"{common_task_config.MONITOR_URI}/api/v1/tasks",
            json=dict(task_id=task_id, user_id=user_id, log_path=log_path, description=description),
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"register_monitor_log error: {e}")
