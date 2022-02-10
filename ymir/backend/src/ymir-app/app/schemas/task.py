import enum
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator

from app.constants.state import TaskState, TaskType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class MergeStrategy(enum.IntEnum):
    stop_upon_conflict = 1
    prefer_newest = 2
    prefer_oldest = 3


class TaskBase(BaseModel):
    name: str
    type: TaskType


class TaskParameter(BaseModel):
    include_datasets: Optional[List[int]]
    include_train_datasets: Optional[List[int]]
    include_validation_datasets: Optional[List[int]]
    include_test_datasets: Optional[List[int]]
    exclude_datasets: Optional[List[int]]

    include_classes: Optional[List[str]]
    exclude_classes: Optional[List[str]]

    # strategy
    strategy: Optional[MergeStrategy] = Field(
        MergeStrategy.prefer_newest, description="strategy to merge multiple datasets"
    )

    # label
    extra_url: Optional[str]
    labellers: Optional[List[EmailStr]]
    keep_annotations: Optional[bool]

    # training
    network: Optional[str]
    backbone: Optional[str]
    hyperparameter: Optional[str]

    # mining
    model_id: Optional[int]
    mining_algorithm: Optional[str]
    top_k: Optional[int]
    generate_annotations: Optional[bool]

    # training & mining & infer
    docker_image: Optional[str]
    # todo replace docker_image with docker_image_id
    docker_image_id: Optional[int]


class TaskCreate(TaskBase):
    parameters: Optional[TaskParameter] = Field(
        None, description="task specific parameters"
    )
    config: Optional[Union[str, Dict]] = Field(
        None, description="docker runtime configuration"
    )

    @validator("config")
    def dumps_config(
        cls, v: Optional[Union[str, Dict]], values: Dict[str, Any]
    ) -> Optional[str]:
        if isinstance(v, dict):
            return json.dumps(v)
        else:
            return v


class TaskUpdate(BaseModel):
    name: str


class TaskInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, TaskBase):
    hash: str
    state: Optional[TaskState] = TaskState.pending
    error_code: Optional[str]
    duration: Optional[int] = Field(0, description="task process time in seconds")
    progress: Optional[float] = Field(0, description="from 0 to 100")
    parameters: Optional[str] = Field(
        description="json dumped input parameters when creating task"
    )
    config: Optional[str] = Field(
        description="json dumped docker runtime configuration"
    )
    user_id: int = Field(description="task owner's user_id")

    last_message_datetime: datetime = None  # type: ignore

    @validator("last_message_datetime", pre=True)
    def default_datetime(
        cls,
        value: datetime,  # noqa: N805, WPS110
    ) -> datetime:
        return value or datetime.now()

    class Config:
        orm_mode = True


class TaskResult(BaseModel):
    dataset_id: Optional[int]
    model_id: Optional[int]
    error: Optional[Dict]


class TaskInternal(TaskInDBBase):
    parameters: Optional[str]
    result: Optional[TaskResult]
    config: Optional[str]
    state: TaskState

    @validator("parameters")
    def loads_parameters(cls, v: str) -> Dict[str, Any]:
        if not v:
            return {}
        return json.loads(v)

    @validator("config")
    def loads_config(cls, v: str) -> Dict[str, Any]:
        if not v:
            return {}
        return json.loads(v)


class Task(TaskInternal):
    @validator("state")
    def merge_state(cls, v: TaskState) -> TaskState:
        """
        Frontend doesn't differentiate premature and terminated
        """
        if v is TaskState.premature:
            v = TaskState.terminate
        return v


class Tasks(BaseModel):
    total: int
    items: List[Task]


class TaskTerminate(BaseModel):
    fetch_result: Optional[bool] = True


class TaskUpdateStatus(BaseModel):
    hash: str
    timestamp: float
    percent: Optional[float] = 0
    state: TaskState
    state_code: Optional[str]
    state_message: Optional[str]


class TaskOut(Common):
    result: Task


class TasksOut(Common):
    result: Tasks
