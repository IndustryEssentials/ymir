from typing import Any, List, Optional

from pydantic import BaseModel, Field, root_validator, validator
from app.config import settings
from app.constants.state import ResultState, TaskType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.task import TaskInternal


def get_model_url(model_hash: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-models/{model_hash}"


class ModelBase(BaseModel):
    hash: Optional[str] = None
    source: TaskType
    description: Optional[str]
    map: Optional[float] = Field(description="Mean Average Precision")
    result_state: ResultState = ResultState.processing
    model_group_id: int
    project_id: int
    task_id: Optional[int]
    user_id: Optional[int]


class ModelImport(BaseModel):
    project_id: int
    group_name: str = Field(description="Model Group Name")
    description: Optional[str]
    input_model_path: Optional[str] = Field(description="from uploaded file url")
    input_model_id: Optional[int] = Field(description="from model of other user")
    input_url: Optional[str] = Field(description="model url")
    source: Optional[TaskType]
    import_type: Optional[TaskType]

    @validator("import_type", "source", pre=True, always=True)
    def gen_import_type(cls, v: TaskType, values: Any) -> TaskType:
        if values.get("input_model_id"):
            return TaskType.copy_model
        elif values.get("input_model_path") or values.get("input_url"):
            return TaskType.import_model
        else:
            raise ValueError("Missing input source")


class ModelCreate(ModelBase):
    task_id: int
    user_id: int


class ModelUpdate(BaseModel):
    name: str
    description: Optional[str]


class ModelInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ModelBase):
    name: str
    group_name: str
    version_num: int
    related_task: Optional[TaskInternal]
    is_visible: bool

    class Config:
        orm_mode = True


# Properties to return to caller
class Model(ModelInDBBase):
    url: Optional[str] = None

    @root_validator
    def make_up_url(cls, values: Any) -> Any:
        # make up the model url
        if values.get("hash"):
            values["url"] = get_model_url(values["hash"])
        return values


class ModelPagination(BaseModel):
    total: int
    items: List[Model]


class ModelOut(Common):
    result: Model


class ModelsOut(Common):
    result: List[Model]


class ModelPaginationOut(Common):
    result: ModelPagination
