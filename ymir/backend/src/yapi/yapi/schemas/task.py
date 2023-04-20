from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field, root_validator, constr, conint
from yapi.constants.state import (
    TaskType,
    ImportStrategy,
    ResultType,
    TaskState,
)
from yapi.utils.data import exclude_nones
from yapi.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    generate_uuid,
)


class TaskResult(BaseModel):
    id: int = Field(description="dataset / model / prediction / docker image id")
    version_id: Optional[int] = Field(description="dataset / model version id")
    type: ResultType = Field(description="result type: dataset / model / prediction / docker image")


class TaskBase(BaseModel):
    type: int = Field(description="task type")
    state: int
    error_code: int = 0
    duration: int
    percent: float
    user_id: int
    is_terminated: bool
    result: Optional[TaskResult]

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        if "result" in values:
            del values["result"]

        if values["state"] == TaskState.done or values["state"] == TaskState.terminate:
            if values.get("result_dataset"):
                type_ = ResultType.dataset.value
                id_ = values["result_dataset"]["dataset_group_id"]
                version_id = values["result_dataset"]["id"]
            elif values.get("result_prediction"):
                type_ = ResultType.prediction.value
                id_ = values["result_prediction"]["id"]
                version_id = None
            elif values.get("result_model"):
                type_ = ResultType.model.value
                id_ = values["result_model"]["model_group_id"]
                version_id = values["result_model"]["id"]
            if values.get("result_docker_image"):
                type_ = ResultType.docker_image.value
                id_ = values["result_docker_image"]["id"]
                version_id = None
            else:
                type_, id_, version_id = ResultType.no_result.value, -1, -1
            values["result"] = {
                "type": type_,
                "id": id_,
                "version_id": version_id,
            }

        values["error_code"] = values.get("error_code") or 0
        values["duration"] = values.get("duration") or 0

        return values


class Task(IdModelMixin, DateTimeModelMixin, TaskBase):
    pass


class TaskPagination(BaseModel):
    total: int
    items: List[Task]


class TaskPaginationOut(Common):
    result: TaskPagination


class TaskOut(Common):
    result: Task


class ResourceParams(BaseModel):
    gpu_count: Optional[conint(ge=0)]


class TrainTaskRequest(BaseModel):
    project_id: int
    class_names: List[constr(min_length=1, strip_whitespace=True)]
    dataset_version_id: int
    docker_image_config: Dict[str, Any]
    docker_image_id: int
    model_version_id: Optional[int]
    validation_dataset_version_id: int
    resource_params: Optional[ResourceParams]


class InferenceTaskRequest(BaseModel):
    project_id: int
    dataset_version_id: int
    docker_image_config: Optional[Dict[str, Any]]
    docker_image_id: Optional[int]
    model_version_id: int
    resource_params: Optional[ResourceParams]


class MineTaskRequest(BaseModel):
    project_id: int
    dataset_version_id: int
    docker_image_config: Optional[Dict[str, Any]]
    docker_image_id: Optional[int]
    model_version_id: int
    top_k: int
    resource_params: Optional[ResourceParams]


class ImportDatasetRequest(BaseModel):
    project_id: int
    input_dataset_version_id: Optional[str]
    input_path: Optional[str]
    input_url: Optional[str]


class ImportModelRequest(BaseModel):
    project_id: int
    input_model_version_id: Optional[int]
    input_url: Optional[str]


class LabelDatasetRequest(BaseModel):
    project_id: int
    class_names: List[constr(min_length=1, strip_whitespace=True)]
    dataset_version_id: int
    doc_url: Optional[str]
    labellers: Optional[List[str]]
    preannotation: int


class MergeDatasetsRequest(BaseModel):
    project_id: int
    dataset_id: int
    dataset_version_ids: List[int]


class ExcludeDatasetsRequest(BaseModel):
    project_id: int
    dataset_version_id: int
    exclude_dataset_version_ids: List[int]


class ExcludeDatasetsRequestHelper(ExcludeDatasetsRequest):
    dataset_version_ids: List[int]

    @root_validator(pre=True)
    def convert_parameters(cls, values: Any) -> Any:
        values["dataset_version_ids"] = [values["dataset_version_id"]]
        return values


class SampleDatasetRequest(BaseModel):
    project_id: int
    dataset_version_id: int
    sampling_count: int


class FilterDatasetRequest(BaseModel):
    project_id: int
    dataset_version_id: int
    include_class_names: Optional[List[constr(min_length=1, strip_whitespace=True)]]
    exclude_class_names: Optional[List[constr(min_length=1, strip_whitespace=True)]]


class ImportDockerImageRequest(BaseModel):
    url: constr(min_length=1, strip_whitespace=True)


class RefreshDockerImageRequest(BaseModel):
    docker_image_id: int


class AppTaskAdapter(BaseModel):
    name: str
    project_id: int
    type: TaskType
    parameters: Dict
    docker_image_config: Optional[Dict]

    @root_validator(pre=True)
    def convert_parameters(cls, values: Any) -> Any:
        values["name"] = generate_uuid()
        if values.get("resource_params") and values["resource_params"].get("gpu_count"):
            docker_image_config = values.get("docker_image_config", {})
            values["docker_image_config"] = {
                "gpu_count": values["resource_params"]["gpu_count"],
                **docker_image_config,
            }
        values["parameters"] = exclude_nones(
            {
                "task_type": values["type"].name,
                "project_id": values["project_id"],
                "model_id": values.get("model_version_id"),
                "model_stage_id": values.get("model_stage_id"),
                "dataset_id": values.get("dataset_version_id"),
                "validation_dataset_id": values.get("validation_dataset_version_id"),
                "docker_image_id": values.get("docker_image_id"),
                "keywords": values.get("class_names"),
                "top_k": values.get("top_k"),
                "labellers": values.get("labellers"),
                "extra_url": values.get("doc_url"),
                "annotation_type": 1 if values.get("preannotation") else None,
                "include_datasets": values.get("dataset_version_ids"),
                "dataset_group_id": values.get("dataset_id"),
                "exclude_datasets": values.get("exclude_dataset_version_ids"),
                "sampling_count": values.get("sampling_count"),
                "include_labels": values.get("include_class_names"),
                "exclude_labels": values.get("exclude_class_names"),
            }
        )
        return values


class CreateResourceResponse(Common):
    result: int  # task_id

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        result = values.get("result")
        if isinstance(result, dict):
            values["result"] = result.get("task_id", -1)
        else:
            values["result"] = -1
        return values


class CreateTaskResponse(Common):
    result: int  # task_id

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        result = values.get("result")
        if isinstance(result, dict):
            values["result"] = result.get("id", -1)
        else:
            values["result"] = -1
        return values


class AppImportOpsAdapter(BaseModel):
    project_id: int
    group_name: Optional[str]
    input_path: Optional[str]
    input_url: Optional[str]
    input_dataset_id: Optional[int]
    input_model_id: Optional[int]
    input_model_path: Optional[str]
    strategy: int = ImportStrategy.add_unknown_annotations

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        values["group_name"] = generate_uuid()

        if values.get("input_dataset_version_id"):
            values["input_dataset_id"] = values["input_dataset_version_id"]
        if values.get("input_model_version_id"):
            values["input_model_id"] = values["input_model_version_id"]
        return values
