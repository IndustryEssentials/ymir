from enum import IntEnum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ResultType(IntEnum):
    no_result = 0
    dataset = 1
    model = 2


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

    result_type: Optional[int]
    result_id: Optional[int]
    result_state: Optional[int]

    def update_with_app_response(self, result: Dict) -> None:
        result_type = ResultType(result["result_type"])
        if result_type is ResultType.dataset:
            result_record = result["result_dataset"]
        elif result_type is ResultType.model:
            result_record = result["result_model"]
        else:
            return
        self.result_type = result["result_type"]
        self.result_id = result_record["id"]
        self.result_state = result_record["result_state"]


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
