from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TaskStateExtra(BaseModel):
    user_id: str


class TaskStatePercent(BaseModel):
    task_id: str
    timestamp: float = Field(gt=0)
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


# data models: resp
class EventResp(BaseModel):
    return_code: int
    return_msg: str
