from typing import List

from pydantic import BaseModel

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.task import Task


class VisualizationBase(BaseModel):
    user_id: int
    tid: str

    class Config:
        use_enum_values = True
        validate_all = True


class VisualizationInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, VisualizationBase):
    tasks: List[Task]

    class Config:
        orm_mode = True


class VisualizationCreate(BaseModel):
    task_ids: List[int]

    class Config:
        use_enum_values = True
        validate_all = True


class VisualizationUpdate(VisualizationBase):
    pass


# Properties to return to caller
class Visualization(VisualizationInDBBase):
    pass


class VisualizationOut(Common):
    result: Visualization


class VisualizationPagination(BaseModel):
    total: int
    items: List[Visualization]


class VisualizationPaginationOut(Common):
    result: VisualizationPagination
