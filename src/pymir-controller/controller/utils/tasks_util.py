from datetime import datetime

from controller.utils import code
from proto import backend_pb2


def task_state_str_to_code(state: str) -> backend_pb2.TaskState:
    _task_state_to_enum = {
        "pending": backend_pb2.TaskStatePending,
        "running": backend_pb2.TaskStateRunning,
        "runing": backend_pb2.TaskStateRunning,
        "done": backend_pb2.TaskStateDone,
        "error": backend_pb2.TaskStateError,
    }
    return _task_state_to_enum[state]


def task_state_code_to_str(state: backend_pb2.TaskState) -> str:
    _dict_enum_to_str = {
        backend_pb2.TaskStatePending: "pending",
        backend_pb2.TaskStateRunning: "running",
        backend_pb2.TaskStateDone: "done",
        backend_pb2.TaskStateError: "error",
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
