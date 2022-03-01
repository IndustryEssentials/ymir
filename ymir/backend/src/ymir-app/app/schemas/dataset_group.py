from typing import List

from pydantic import BaseModel, Field

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.dataset import Dataset


class DatasetGroupBase(BaseModel):
    name: str = Field(description="Dataset Group Name")
    project_id: int


class DatasetGroupCreate(DatasetGroupBase):
    pass


class DatasetGroupUpdate(BaseModel):
    name: str


class DatasetGroupInDBBase(
    IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, DatasetGroupBase
):
    datasets: List[Dataset]

    class Config:
        orm_mode = True


class DatasetGroup(DatasetGroupInDBBase):
    pass


class DatasetGroupPagination(BaseModel):
    total: int
    items: List[DatasetGroup]


class DatasetGroupOut(Common):
    result: DatasetGroup


class DatasetGroupsOut(Common):
    result: List[DatasetGroup]


class DatasetGroupPaginationOut(Common):
    result: DatasetGroupPagination
