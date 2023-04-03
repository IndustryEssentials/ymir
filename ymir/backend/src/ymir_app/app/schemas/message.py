from typing import List, Optional

from pydantic import BaseModel

from app.constants.state import TaskState, TaskType
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
    dataset_id: int
    model_id: int
    prediction_id: int
    is_read: bool = False


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    is_read: bool


class MessageInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, MessageBase):
    pass


class MessageInDB(MessageInDBBase):
    pass


class Message(MessageInDB):
    pass


class MessagesOut(Common):
    result: List[Message]
