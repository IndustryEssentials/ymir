import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator

from app.config import settings
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class ModelBase(BaseModel):
    hash: str
    name: str
    map: Optional[str] = Field(description="Mean Average Precision")
    parameters: Optional[str] = Field(
        description="input parameters of related training task"
    )
    task_id: Optional[int]
    user_id: Optional[int]


class ModelCreate(ModelBase):
    pass


class ModelImport(BaseModel):
    hash: str
    name: str
    map: Optional[str]
    parameters: Optional[str]
    input_url: str


class ModelUpdate(BaseModel):
    name: str


class ModelInDB(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ModelBase):
    class Config:
        orm_mode = True


class Model(ModelInDB):
    parameters: Optional[Any] = None
    config: Optional[Any] = None
    keywords: Optional[List[str]] = None
    source: Optional[int] = None
    task_type: Optional[int] = None
    task_name: Optional[str] = None
    task_id: Optional[int] = None
    task_parameters: Optional[Any] = None
    task_config: Optional[Any] = None

    url: Optional[str] = None

    @root_validator
    def make_up_fields(cls, values: Any) -> Any:
        parameters = values["parameters"] or values.pop("task_parameters", None)
        values["parameters"] = parse_optional_json(parameters)
        values["keywords"] = extract_keywords(parameters)
        values["config"] = parse_optional_json(values.pop("task_config", None))

        # the source of a model is actually the task
        # that import the model, copy the model or
        # train the model
        values["source"] = values.get("task_type")
        # make up the model url
        if values.get("hash"):
            values["url"] = get_model_url(values["hash"])
        return values


def parse_optional_json(j: Optional[str]) -> Dict:
    return json.loads(j) if j is not None else {}


def get_model_url(model_hash: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-models/{model_hash}"


def extract_keywords(parameters: Optional[Union[str, Dict]]) -> List:
    if not parameters:
        return []
    if isinstance(parameters, str):
        parameters = json.loads(parameters)
    return parameters.get("include_classes", [])  # type: ignore


class Models(BaseModel):
    total: int
    items: List[Model]


class ModelOut(Common):
    result: Model


class ModelsOut(Common):
    result: List[Model]


class ModelPaginationOut(Common):
    result: Models
