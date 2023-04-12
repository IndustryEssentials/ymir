from typing import Any, List, Optional

from pydantic import BaseModel, root_validator

from app.constants.state import TaskState, TaskType, ResultType, ResultState
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class MessageBase(BaseModel):
    user_id: int
    project_id: int

    state: Optional[TaskState]
    task_type: Optional[TaskType]
    content: Optional[str] = None
    dataset_id: Optional[int]
    model_id: Optional[int]
    prediction_id: Optional[int]
    is_read: bool = False


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    is_read: bool


class MessageInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, MessageBase):
    class Config:
        orm_mode = True


class MessageInDB(MessageInDBBase):
    pass


class TaskResult(BaseModel):
    id: int
    type: ResultType
    state: ResultState


class Message(MessageInDB):
    result: TaskResult

    @root_validator(pre=True)
    def gen_result_type(cls, values: Any) -> Any:
        values = dict(values)
        if values.get("dataset_id"):
            id_ = values["dataset_id"]
            type_ = ResultType.dataset
            state = values["dataset"].result_state
        elif values.get("model_id"):
            id_ = values["model_id"]
            type_ = ResultType.model
            state = values["model"].result_state
        elif values.get("prediction_id"):
            id_ = values["prediction_id"]
            type_ = ResultType.prediction
            state = values["prediction"].result_state
        else:
            raise ValueError("Message relates to invalid result")
        values["result"] = TaskResult(id=id_, type=type_, state=state)
        return values


class MessageOut(Common):
    result: Message


class MessagesOut(Common):
    result: List[Message]


class MessagePagination(BaseModel):
    total: int
    items: List[Message]


class MessagePaginationOut(Common):
    result: MessagePagination
