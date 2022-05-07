from typing import List, Optional

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
    user_id: int
    description: Optional[str]


class DatasetGroupCreate(DatasetGroupBase):
    pass


class DatasetGroupUpdate(BaseModel):
    name: str


class DatasetGroupInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, DatasetGroupBase):
    datasets: List[Dataset]
    is_visible: bool

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
