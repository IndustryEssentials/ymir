from typing import Any, List, Optional

from pydantic import BaseModel, root_validator
from yapi.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
)


class ModelBase(BaseModel):
    """
    name, project_id, user_id, description are all hide
    """


class Model(IdModelMixin, DateTimeModelMixin, ModelBase):
    training_dataset_version_id: Optional[int]

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        values["training_dataset_version_id"] = values.get("training_dataset_id")
        return values


class ModelPagination(BaseModel):
    total: int
    items: List[Model]


class ModelPaginationOut(Common):
    result: ModelPagination


class ModelOut(Common):
    result: Model


class ModelVersionBase(BaseModel):
    pass


class ModelVersion(ModelVersionBase, IdModelMixin, DateTimeModelMixin):
    task_id: int
    result_state: int
    object_type: int
    class_names: Optional[List[str]]

    map: Optional[float]
    miou: Optional[float]
    mask_ap: Optional[float]

    url: str

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        values["class_names"] = values.get("keywords")
        return values


class ModelVersionOut(Common):
    result: ModelVersion


class ModelVersionPagination(BaseModel):
    total: int
    items: List[ModelVersion]


class ModelVersionPaginationOut(Common):
    result: ModelVersionPagination
