import enum
import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Optional, Union
from operator import attrgetter

from typing_extensions import Annotated

from pydantic import BaseModel, EmailStr, Field, validator, root_validator

from app.constants.state import AnnotationType, MiningStrategy, ResultType, TaskState, TaskType
from app.api.errors.errors import DockerImageNotFound
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    DatasetResult,
    ModelResult,
    IdModelMixin,
    IsDeletedModelMixin,
    IterationContext,
    TypedDataset,
    TypedModel,
    TypedLabel,
    MergeStrategy,
    dataset_normalize,
    label_normalize,
    model_normalize,
)
from id_definition.task_id import TaskId


class TaskBase(BaseModel):
    name: str = ""
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


class TaskParameterBase(BaseModel):
    dataset_id: int
    dataset_group_id: Optional[int]
    dataset_group_name: Optional[str]

    model_id: Optional[int]
    model_stage_id: Optional[int]

    keywords: Optional[List[str]]

    docker_image_id: Optional[int]
    docker_image: Optional[str]
    docker_image_config: Optional[str]

    description: Optional[str]

    typed_datasets: Optional[List[TypedDataset]]
    typed_models: Optional[List[TypedModel]]
    typed_labels: Optional[List[TypedLabel]]

    merge_strategy: Optional[MergeStrategy] = MergeStrategy.prefer_newest

    @validator("keywords")
    def normalize_keywords(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        return [keyword.strip() for keyword in v]


class LabelParameter(TaskParameterBase):
    task_type: Literal["label"]

    extra_url: Optional[str]
    labellers: Optional[List[EmailStr]]
    annotation_type: Optional[AnnotationType] = None

    normalize_datasets = root_validator(allow_reuse=True)(dataset_normalize)
    normalize_labels = root_validator(allow_reuse=True)(label_normalize)


class TrainingParameter(TaskParameterBase):
    task_type: Literal["training"]

    validation_dataset_id: Optional[int]
    strategy: Optional[TrainingDatasetsStrategy] = TrainingDatasetsStrategy.stop
    preprocess: Optional[TaskPreprocess] = Field(description="preprocess to apply to related dataset")

    normalize_datasets = root_validator(allow_reuse=True)(dataset_normalize)
    normalize_models = root_validator(allow_reuse=True)(model_normalize)
    normalize_labels = root_validator(allow_reuse=True)(label_normalize)


class MiningParameterBase(TaskParameterBase):
    top_k: Optional[int]
    generate_annotations: Optional[bool]

    normalize_datasets = root_validator(allow_reuse=True)(dataset_normalize)
    normalize_models = root_validator(allow_reuse=True)(model_normalize)
    normalize_labels = root_validator(allow_reuse=True)(label_normalize)


class MiningParameter(MiningParameterBase):
    task_type: Literal["mining"]


class InferParameter(MiningParameterBase):
    task_type: Literal["infer"]


class FusionParameterBase(TaskParameterBase, IterationContext):
    include_datasets: List[int] = []
    exclude_datasets: List[int] = []

    include_labels: List[str] = []
    exclude_labels: List[str] = []

    sampling_count: int = 0

    normalize_datasets = root_validator(allow_reuse=True)(dataset_normalize)
    normalize_labels = root_validator(allow_reuse=True)(label_normalize)

    class Config:
        # when add new exclude_datasets, update normalize_datasets as well
        validate_assignment = True

    def update_with_iteration_context(self, iterations_getter: Callable) -> None:
        if not self.exclude_last_result:
            return
        iterations = iterations_getter(project_id=self.project_id)

        if self.mining_strategy == MiningStrategy.chunk:
            datasets_to_exclude = [i.mining_input_dataset_id for i in iterations if i.mining_input_dataset_id]
        elif self.mining_strategy == MiningStrategy.dedup:
            datasets_to_exclude = [i.mining_output_dataset_id for i in iterations if i.mining_output_dataset_id]
        else:
            return
        datasets_to_exclude += self.exclude_datasets
        self.exclude_datasets = list(set(datasets_to_exclude))
        return


class FusionParameter(FusionParameterBase):
    task_type: Literal["fusion"]


class MergeParameter(FusionParameterBase):
    task_type: Literal["merge"]

    @root_validator(pre=True)
    def fill_in_dataset_id(cls, values: Any) -> Any:
        if not values.get("dataset_id"):
            values["dataset_id"] = values["include_datasets"][0]
        return values


class FilterParameter(FusionParameterBase):
    task_type: Literal["filter"]


TaskParameter = Annotated[
    Union[
        LabelParameter,
        TrainingParameter,
        MiningParameter,
        InferParameter,
        FusionParameter,
        MergeParameter,
        FilterParameter,
    ],
    Field(description="Generic Task Parameters", discriminator="task_type"),  # noqa: F722, F821
]


def fillin_dataset_hashes(datasets_getter: Callable, typed_datasets: List[TypedDataset]) -> None:
    if not typed_datasets:
        return
    datasets_in_db = datasets_getter(dataset_ids=[i.id for i in typed_datasets])
    data = {d.id: (d.hash, d.create_datetime, d.name) for d in datasets_in_db}
    for dataset in typed_datasets:
        dataset.hash, dataset.create_datetime, dataset.name = data[dataset.id]


def fillin_model_hashes(model_stages_getter: Callable, typed_models: List[TypedModel]) -> None:
    if not typed_models:
        return
    model_stages_in_db = model_stages_getter(ids=[i.stage_id for i in typed_models if i.stage_id])
    data = {stage.id: (stage.model.hash, stage.name) for stage in model_stages_in_db}  # type: ignore
    for model in typed_models:
        model.hash, model.stage_name = data[model.stage_id]


def fillin_label_ids(labels_getter: Callable, typed_labels: List[TypedLabel]) -> None:
    if not typed_labels:
        return
    class_ids = labels_getter([i.name for i in typed_labels])
    for label, class_id in zip(typed_labels, class_ids):
        label.class_id = class_id


class TaskCreate(TaskBase):
    parameters: TaskParameter
    docker_image_config: Optional[Dict] = Field(description="docker runtime configuration")

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def tuck_into_parameters(cls, values: Any) -> Any:
        """
        For frontend, docker image config is a separate task configuration,
        however, the underlying controller treat docker image config as parameter
        so we just tuck docker image config into task_parameter
        """
        if values.get("docker_image_config"):
            values["parameters"]["docker_image_config"] = json.dumps(values["docker_image_config"])
        return values

    def fulfill_parameters(
        self,
        datasets_getter: Callable,
        model_stages_getter: Callable,
        iterations_getter: Callable,
        labels_getter: Callable,
        docker_image_getter: Callable,
    ) -> None:
        """
        Update task parameters when database and user_labels are ready
        """
        # extra logic for dataset fusion:
        #   reorder datasets based on merge_strategy
        if isinstance(self.parameters, FusionParameter) and self.parameters.typed_datasets:
            self.parameters.update_with_iteration_context(iterations_getter)

        if self.parameters.typed_datasets:
            fillin_dataset_hashes(datasets_getter, self.parameters.typed_datasets)
            if self.parameters.merge_strategy:
                self.parameters.typed_datasets.sort(
                    key=attrgetter("create_datetime"),
                    reverse=(self.parameters.merge_strategy == MergeStrategy.prefer_newest),
                )

        if self.parameters.typed_labels:
            fillin_label_ids(labels_getter, self.parameters.typed_labels)
        if self.parameters.typed_models:
            fillin_model_hashes(model_stages_getter, self.parameters.typed_models)
        if self.parameters.docker_image_id:
            docker_image = docker_image_getter(self.parameters.docker_image_id)
            if not docker_image:
                raise DockerImageNotFound()
            self.parameters.docker_image = docker_image.url


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
