import json
import enum
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator

from app.models.task import TaskState, TaskType
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

    # training
    network: Optional[str]
    backbone: Optional[str]
    hyperparameter: Optional[str]

    # mining
    model_id: Optional[int]
    mining_algorithm: Optional[str]
    top_k: Optional[int]


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
    progress: Optional[float] = Field(0, description="from 0 to 100")
    parameters: Optional[str] = Field(
        description="json dumped input parameters when creating task"
    )
    config: Optional[str] = Field(
        description="json dumped docker runtime configuration"
    )
    user_id: int = Field(description="task owner's user_id")

    class Config:
        orm_mode = True


class TaskResult(BaseModel):
    dataset_id: Optional[int]
    model_id: Optional[int]
    error: Optional[Dict]


class Task(TaskInDBBase):
    parameters: Optional[str]
    result: Optional[TaskResult]
    config: Optional[str]

    @validator("parameters")
    def loads_parameters(cls, v: str, values: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            return {}
        return json.loads(v)

    @validator("config")
    def loads_config(cls, v: str, values: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            return {}
        return json.loads(v)


class Tasks(BaseModel):
    total: int
    items: List[Task]


class TaskOut(Common):
    result: Union[Task, Tasks]
