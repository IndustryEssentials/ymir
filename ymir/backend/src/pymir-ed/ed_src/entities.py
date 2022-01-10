from typing import List, Optional

from pydantic import BaseModel

from proto import backend_pb2 as mirsvrpb


# data models: req
class TaskStateExtra(BaseModel):
    user_id: str
    monitor_type: int
    log_path: List[str]
    description: Optional[str]


class TaskStatePercent(BaseModel):
    task_id: str
    timestamp: int
    percent: float
    state: str
    state_code: int
    state_message: Optional[str]
    stack_error_info: Optional[str]


class TaskState(BaseModel):
    task_extra_info: TaskStateExtra
    percent_result: TaskStatePercent


# data models: resp
class EventResp(BaseModel):
    return_code: int
    return_msg: str


def task_state_str_to_enum(state: str) -> int:
    d = {
        'unknown': mirsvrpb.TaskState.TaskStateUnknown,
        'pending': mirsvrpb.TaskState.TaskStatePending,
        'running': mirsvrpb.TaskState.TaskStateRunning,
        'done': mirsvrpb.TaskState.TaskStateDone,
        'error': mirsvrpb.TaskState.TaskStateError,
        'miss': mirsvrpb.TaskState.TaskStateMiss,
    }
    return d[state]
