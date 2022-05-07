from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.model import Model


class ModelGroupBase(BaseModel):
    name: str = Field(description="Model Group Name")
    project_id: int
    training_dataset_id: Optional[int]


class ModelGroupCreate(ModelGroupBase):
    description: Optional[str]


class ModelGroupUpdate(BaseModel):
    name: str


class ModelGroupInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ModelGroupBase):
    models: List[Model]
    is_visible: bool

    class Config:
        orm_mode = True


class ModelGroup(ModelGroupInDBBase):
    pass


class ModelGroupPagination(BaseModel):
    total: int
    items: List[ModelGroup]


class ModelGroupOut(Common):
    result: ModelGroup


class ModelGroupsOut(Common):
    result: List[ModelGroup]


class ModelGroupPaginationOut(Common):
    result: ModelGroupPagination
