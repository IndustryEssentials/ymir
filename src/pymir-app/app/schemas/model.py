import json
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field, root_validator, validator

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
    user_id: int


class ModelInput(BaseModel):
    name: str = Field(description="dataset name")
    input_url: Optional[AnyHttpUrl] = Field(description="from url")
    input_model_id: Optional[int] = Field(description="from other's model")
    input_token: Optional[str] = Field(description="from uploaded file token")

    @root_validator
    def check_input_source(cls, values: Any) -> Any:
        fields = ("input_url", "input_model_id", "input_token")
        if all(values.get(i) is None for i in fields):
            raise ValueError("Missing input source")
        return values


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: str


class ModelInDB(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ModelBase):
    class Config:
        orm_mode = True


class Model(ModelInDB):
    parameters: Optional[Any] = None
    config: Optional[Any] = None
    keywords: Optional[Any] = None
    source: Optional[int] = None
    task_type: Optional[int] = None
    task_name: Optional[str] = None
    task_id: Optional[int] = None
    task_parameters: Optional[Any] = None
    task_config: Optional[Any] = None

    url: Optional[str] = None

    @root_validator
    def make_up_fields(cls, values: Any) -> Any:
        raw = values.pop("task_parameters", None)
        parameters = json.loads(raw) if raw else {}
        values["parameters"] = parameters

        task_config_str = values.pop("task_config", None)
        task_config = json.loads(task_config_str) if task_config_str else {}
        values["config"] = task_config

        values["keywords"] = parameters.get("include_classes", [])
        # the source of a model is actually the task
        # that import the model, copy the model or
        # train the model
        values["source"] = values.get("task_type")
        # make up the model url
        if values.get("hash"):
            values["url"] = get_model_url(values["hash"])
        return values


def get_model_url(model_hash: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-models/{model_hash}"


class Models(BaseModel):
    total: int
    items: List[Model]


class ModelOut(Common):
    result: Union[Model, Models, List[Model]]
