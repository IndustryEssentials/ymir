from datetime import datetime

from controller.utils import code
from ymir.protos import mir_common_pb2 as mir_common


def task_state_str_to_code(state: str) -> mir_common.TaskState:
    _task_state_to_enum = {
        "pending": mir_common.TaskStatePending,
        "running": mir_common.TaskStateRunning,
        "runing": mir_common.TaskStateRunning,
        "done": mir_common.TaskStateDone,
        "error": mir_common.TaskStateError,
    }
    return _task_state_to_enum[state]


def task_state_code_to_str(state: mir_common.TaskState) -> str:
    _dict_enum_to_str = {
        mir_common.TaskStatePending: "pending",
        mir_common.TaskStateRunning: "running",
        mir_common.TaskStateDone: "done",
        mir_common.TaskStateError: "error",
    }
    return _dict_enum_to_str[state]


def write_task_progress(monitor_file: str,
                        tid: str,
                        percent: float,
                        state: mir_common.TaskState,
                        msg: str = None) -> code.ResCode:
    if not monitor_file:
        raise RuntimeError("Invalid monitor_file")
    with open(monitor_file, 'w') as f:
        f.write('\t'.join([tid, str(int(datetime.now().timestamp())), str(percent), task_state_code_to_str(state)]))
        if msg:
            f.write('\n{}'.format(msg))
    return code.ResCode.CTR_OK
