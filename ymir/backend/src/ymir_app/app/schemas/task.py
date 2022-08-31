import enum
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator, root_validator

from app.constants.state import AnnotationType, TaskState, TaskType, ResultState, ResultType, IterationStage
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from id_definition.task_id import TaskId


class TaskBase(BaseModel):
    name: str
    type: TaskType
    project_id: int

    class Config:
        use_enum_values = True


class TrainingDatasetsStrategy(enum.IntEnum):
    stop = 0
    as_training = 1  # use duplicated assets as training assets
    as_validation = 2  # use duplicated assets as validation assets


class LongsideResizeParameter(BaseModel):
    dest_size: int


class TaskPreprocess(BaseModel):
    longside_resize: LongsideResizeParameter


class TaskParameter(BaseModel):
    dataset_id: int
    keywords: Optional[List[str]]

    # label
    extra_url: Optional[str]
    labellers: Optional[List[EmailStr]]
    annotation_type: Optional[AnnotationType] = None

    # training
    validation_dataset_id: Optional[int]
    network: Optional[str]
    backbone: Optional[str]
    hyperparameter: Optional[str]
    strategy: Optional[TrainingDatasetsStrategy] = TrainingDatasetsStrategy.stop
    preprocess: Optional[TaskPreprocess] = Field(description="preprocess to apply to related dataset")

    # mining & dataset_infer
    model_id: Optional[int]
    model_stage_id: Optional[int]
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
    iteration_id: Optional[int]
    iteration_stage: Optional[IterationStage]
    parameters: TaskParameter = Field(description="task specific parameters")
    docker_image_config: Optional[Dict] = Field(description="docker runtime configuration")
    preprocess: Optional[TaskPreprocess] = Field(description="preprocess to apply to related dataset")
    result_description: Optional[str] = Field(description="description for task result, not task itself")

    @validator("docker_image_config")
    def dumps_docker_image_config(cls, v: Optional[Union[str, Dict]], values: Dict[str, Any]) -> Optional[str]:
        # we don't care what's inside of config
        # just dumps it as string and save to db
        if isinstance(v, dict):
            return json.dumps(v)
        else:
            return v

    @root_validator(pre=True)
    def tuck_preprocess_into_parameters(cls, values: Any) -> Any:
        """
        For frontend, preprocess is a separate task configuration,
        however, the underlying reads preprocess stuff from task_parameter,
        so we just tuck preprocess into task_parameter
        """
        preprocess = values.get("preprocess")
        if preprocess:
            values["parameters"]["preprocess"] = preprocess
        return values

    class Config:
        use_enum_values = True


class BatchTasksCreate(BaseModel):
    payloads: List[TaskCreate]


class TaskUpdate(BaseModel):
    name: str


class TaskInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, TaskBase):
    hash: str
    state: Optional[TaskState] = TaskState.pending
    error_code: Optional[str]
    duration: Optional[int] = Field(0, description="task process time in seconds")
    percent: Optional[float] = Field(0, ge=0, le=1)
    parameters: Optional[str] = Field(description="json dumped input parameters when creating task")
    config: Optional[str] = Field(description="json dumped docker runtime configuration")
    user_id: int = Field(description="task owner's user_id")

    last_message_datetime: Optional[datetime] = None

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
    parameters: Optional[Any]
    config: Optional[Any]
    state: TaskState
    result_type: ResultType = ResultType.no_result

    @validator("parameters", "config")
    def ensure_dict(cls, v: Optional[Union[Dict, str]]) -> Dict[str, Any]:
        if not v:
            return {}
        if isinstance(v, dict):
            return v
        return json.loads(v)

    @validator("result_type", pre=True, always=True)
    def gen_result_type(cls, v: Any, values: Any) -> Optional[ResultType]:
        task_type = values["type"]
        if task_type in [TaskType.training, TaskType.copy_model, TaskType.import_model]:
            return ResultType.model
        elif task_type in [
            TaskType.mining,
            TaskType.dataset_infer,
            TaskType.label,
            TaskType.import_data,
            TaskType.copy_data,
            TaskType.data_fusion,
            TaskType.filter,
            TaskType.merge,
        ]:
            return ResultType.dataset
        else:
            return ResultType.no_result

    class Config:
        use_enum_values = True


class DatasetResult(BaseModel):
    id: int
    dataset_group_id: int
    result_state: ResultState

    class Config:
        orm_mode = True


class ModelResult(BaseModel):
    id: int
    model_group_id: int
    result_state: ResultState

    class Config:
        orm_mode = True


class Task(TaskInternal):
    result_model: Optional[ModelResult]
    result_dataset: Optional[DatasetResult]

    @root_validator
    def ensure_terminate_state(cls, values: Any) -> Any:
        # as long as a task is marked as terminated
        # use terminate as external state
        if values["is_terminated"]:
            values["state"] = TaskState.terminate
        return values

    @root_validator
    def ensure_single_result(cls, values: Any) -> Any:
        if values.get("result_model") and values.get("result_dataset"):
            raise ValueError("Invalid Task Result")
        return values


class TaskTerminate(BaseModel):
    fetch_result: bool = True


class TaskMonitorPercent(BaseModel):
    task_id: str  # underlying task_id
    timestamp: float
    percent: float
    state: int
    state_code: Optional[int]
    state_message: Optional[str]
    stack_error_info: Optional[str]


class TaskMonitorExtra(BaseModel):
    user_id: str  # underlying user_id


class TaskMonitorEvent(BaseModel):
    task_extra_info: TaskMonitorExtra
    percent_result: TaskMonitorPercent


class TaskMonitorEvents(BaseModel):
    events: List[TaskMonitorEvent]


class TaskUpdateStatus(BaseModel):
    user_id: int
    hash: str
    timestamp: float
    percent: Optional[float] = 0
    state: TaskState
    state_code: Optional[str]
    state_message: Optional[str]

    @classmethod
    def from_monitor_event(cls, msg: str) -> "TaskUpdateStatus":
        payload = json.loads(msg)
        event = payload["percent_result"]
        user_id = int(TaskId.from_task_id(event["task_id"]).user_id)
        return cls(
            user_id=user_id,
            hash=event["task_id"],
            timestamp=event["timestamp"],
            percent=event["percent"],
            state=event["state"],
            state_code=event["state_code"],
            state_message=event["state_message"],
        )


class TaskResultUpdateMessage(BaseModel):
    task_id: str
    timestamp: float
    percent: float
    state: int
    result_state: Optional[int]
    result_model: Optional[ModelResult]
    result_dataset: Optional[DatasetResult]

    @root_validator(pre=True)
    def gen_result_state(cls, values: Any) -> Any:
        result = values.get("result_model") or values.get("result_dataset")
        if not result:
            raise ValueError("Invalid Task Result")
        values["result_state"] = result.result_state
        return values


class TaskOut(Common):
    result: Task


class TasksOut(Common):
    result: List[Task]


class BatchTasksCreateResults(Common):
    result: List[Optional[Task]]


class TaskPagination(BaseModel):
    total: int
    items: List[Task]


class TaskPaginationOut(Common):
    result: TaskPagination


class PaiTaskStatus(BaseModel):
    position: int
    total_pending_task: int


class PaiTask(Task):
    pai_status: Optional[PaiTaskStatus]


class PaiTaskOut(Common):
    result: PaiTask
