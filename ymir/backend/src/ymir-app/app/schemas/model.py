from typing import Any, List, Optional

from pydantic import BaseModel, Field, root_validator

from app.config import settings
from app.constants.state import ResultState
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
    hash: str
    name: str
    map: Optional[float] = Field(description="Mean Average Precision")
    result_state: ResultState = ResultState.processing
    model_group_id: int
    project_id: int
    task_id: Optional[int]
    user_id: Optional[int]


class ModelImport(ModelBase):
    input_url: Optional[str] = Field(description="from url")
    input_model_id: Optional[int] = Field(description="from model of other user")

    @root_validator
    def check_input_source(cls, values: Any) -> Any:
        fields = ("input_url", "input_model_id")
        if all(values.get(i) is None for i in fields):
            raise ValueError("Missing input source")
        return values


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: str


class ModelInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ModelBase):
    version_num: int
    related_task: Optional[TaskInternal]

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
