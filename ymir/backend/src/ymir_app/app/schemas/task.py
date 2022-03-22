import enum
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator, root_validator

from app.constants.state import TaskState, TaskType, ResultType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class TaskBase(BaseModel):
    name: str
    type: TaskType
    project_id: int

    class Config:
        use_enum_values = True


class TaskParameter(BaseModel):
    dataset_id: int
    keywords: Optional[List[str]]

    # label
    extra_url: Optional[str]
    labellers: Optional[List[EmailStr]]
    keep_annotations: Optional[bool]

    # training
    validation_dataset_id: Optional[int]
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

    @validator("keywords")
    def normalize_keywords(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        return [keyword.strip() for keyword in v]


class TaskCreate(TaskBase):
    parameters: TaskParameter = Field(description="task specific parameters")
    docker_image_config: Optional[Dict] = Field(description="docker runtime configuration")

    @validator("docker_image_config")
    def dumps_docker_image_config(cls, v: Optional[Union[str, Dict]], values: Dict[str, Any]) -> Optional[str]:
        # we don't care what's inside of config
        # just dumps it as string and save to db
        if isinstance(v, dict):
            return json.dumps(v)
        else:
            return v

    class Config:
        use_enum_values = True


class TaskUpdate(BaseModel):
    name: str


class TaskInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, TaskBase):
    hash: str
    state: Optional[TaskState] = TaskState.pending
    error_code: Optional[str]
    duration: Optional[int] = Field(0, description="task process time in seconds")
    percent: Optional[float] = Field(0, description="from 0 to 1")
    parameters: Optional[str] = Field(description="json dumped input parameters when creating task")
    config: Optional[str] = Field(description="json dumped docker runtime configuration")
    user_id: int = Field(description="task owner's user_id")

    last_message_datetime: datetime = None  # type: ignore

    is_terminated: bool = False

    @validator("last_message_datetime", pre=True)
    def default_datetime(
        cls,
        value: datetime,
    ) -> datetime:  # noqa: N805, WPS110
        return value or datetime.now()

    @validator("error_code")
    def remove_zero_error_code(cls, value: Optional[str]) -> Optional[str]:
        if value == "0":
            return None
        else:
            return value

    class Config:
        orm_mode = True
        use_enum_values = True


class TaskInternal(TaskInDBBase):
    parameters: Optional[str]
    config: Optional[str]
    state: TaskState
    result_type: ResultType = ResultType.no_result

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

    @validator("result_type", pre=True, always=True)
    def gen_result_type(cls, v: Any, values: Any) -> Optional[ResultType]:
        task_type = values["type"]
        if task_type in [TaskType.training, TaskType.copy_model, TaskType.import_model]:
            return ResultType.model
        elif task_type in [
            TaskType.mining,
            TaskType.label,
            TaskType.import_data,
            TaskType.copy_data,
            TaskType.data_fusion,
        ]:
            return ResultType.dataset
        else:
            return ResultType.no_result

    class Config:
        use_enum_values = True


class Task(TaskInternal):
    @root_validator
    def ensure_terminate_state(cls, values: Any) -> Any:
        # as long as a task is marked as terminated
        # use terminate as external state
        if values["is_terminated"]:
            values["state"] = TaskState.terminate
        return values


class TaskTerminate(BaseModel):
    fetch_result: bool = True


class TaskUpdateStatus(BaseModel):
    hash: str
    timestamp: float
    percent: Optional[float] = 0
    state: TaskState
    state_code: Optional[str]
    state_message: Optional[str]


class TaskOut(Common):
    result: Task


class TaskPagination(BaseModel):
    total: int
    items: List[Task]


class TaskPaginationOut(Common):
    result: TaskPagination


class CreateDatasetType(enum.IntEnum):
    continued_dataset_group = 0
    new_dataset_group = 1


class TrainDataSet(BaseModel):
    training_dataset_name: str
    training_dataset_group: int
    training_dataset_version: int
