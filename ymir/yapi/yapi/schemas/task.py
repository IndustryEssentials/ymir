from typing import Any, List, Optional

from pydantic import BaseModel, Field, root_validator

from yapi.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
)
from yapi.constants.state import ResultType, TaskState


class TaskResult(BaseModel):
    id: int = Field(description="dataset / model / docker image id")
    version_id: int = Field(description="dataset / model version id")
    type: ResultType = Field(description="result type: dataset / model /docker image")


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
    def AdapteAppResponse(cls, values: Any) -> Any:
        if "result" in values:
            del values["result"]

        if values["state"] == TaskState.done or values["state"] == TaskState.terminate:
            if values.get("result_dataset"):
                type, id, version_id = ResultType.dataset.value, values["result_dataset"]["dataset_group_id"], values[
                    "result_dataset"]["id"]
            elif values.get("result_prediction"):
                type, id, version_id = ResultType.prediction.value, values["result_prediction"]["id"], 0
            elif values.get("result_model"):
                type, id, version_id = ResultType.model.value, values["result_model"]["model_group_id"], values[
                    "result_model"]["id"]
            else:
                type, id, version_id = ResultType.no_result.value, -1, -1
            values["result"] = {
                "type": type,
                "id": id,
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
