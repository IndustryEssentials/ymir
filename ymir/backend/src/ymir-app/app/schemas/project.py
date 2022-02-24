from typing import List, Optional

from pydantic import BaseModel, Field

from app.constants.state import MiningStrategy, TrainingType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class ProjectBase(BaseModel):
    name: str = Field(description="Iteration Name")

    mining_strategy: MiningStrategy = MiningStrategy.chunk
    chunk_size: Optional[int]

    training_type: TrainingType = TrainingType.object_detect
    training_keywords: List[str]

    iteration_target: Optional[int]
    map_target: Optional[float]
    training_dataset_count_target: Optional[int]

    training_dataset_group_id: int


# Sufficient properties to create a project
class ProjectCreate(ProjectBase):
    pass


# Properties that can be changed
class ProjectUpdate(BaseModel):
    iteration_target: Optional[int]
    map_target: Optional[float]
    training_dataset_count_target: Optional[int]

    mining_strategy: MiningStrategy = MiningStrategy.chunk
    chunk_size: Optional[int]
    mining_dataset_id: int
    testing_dataset_id: int


class ProjectInDBBase(
    IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ProjectBase
):
    class Config:
        orm_mode = True


# Properties to return to caller
class Project(ProjectInDBBase):
    pass


class ProjectOut(Common):
    result: Project


class ProjectsOut(Common):
    result: List[Project]


class ProjectPagination(BaseModel):
    total: int
    items: List[Project]


class ProjectPaginationOut(Common):
    result: ProjectPagination
