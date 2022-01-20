from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TaskStateExtra(BaseModel):
    user_id: str


class TaskStatePercent(BaseModel):
    task_id: str
    timestamp: int = Field(gt=0)
    percent: float = Field(ge=0, le=1)
    state: int
    state_code: int
    state_message: Optional[str]
    stack_error_info: Optional[str]


class TaskState(BaseModel):
    task_extra_info: TaskStateExtra
    percent_result: TaskStatePercent


TaskStateDict = Dict[str, TaskState]


class EventPayload(BaseModel):
    event: str
    namespace: Optional[str] = None
    data: dict


EventPayloadList = List[EventPayload]


class TaskStateEventPayloadData(BaseModel):
    state: int
    percent: float
    timestamp: int
    state_code: int
    state_message: str
    stack_error_info: str
    # 'state': taskstate.percent_result.state,
    # 'percent': taskstate.percent_result.percent,
    # 'timestamp': taskstate.percent_result.timestamp,
    # 'state_code': taskstate.percent_result.state_code,
    # 'state_message': taskstate.percent_result.state_message,
    # 'stack_error_info': taskstate.percent_result.stack_error_info


# data models: resp
class EventResp(BaseModel):
    return_code: int
    return_msg: str
