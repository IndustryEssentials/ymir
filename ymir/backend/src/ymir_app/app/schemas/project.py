import json
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.constants.state import MiningStrategy, TrainingType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)

from app.schemas.iteration import IterationInDBBase


class ProjectBase(BaseModel):
    name: str = Field(description="Project Name")
    description: Optional[str]

    mining_strategy: MiningStrategy = MiningStrategy.chunk
    chunk_size: Optional[int] = 0

    training_type: TrainingType = TrainingType.object_detect

    iteration_target: Optional[int]
    map_target: Optional[float]
    training_dataset_count_target: Optional[int]


# Sufficient properties to create a project
class ProjectCreate(ProjectBase):
    training_keywords: List[str]

    class Config:
        use_enum_values = True
        validate_all = True


# Properties that can be changed
class ProjectUpdate(BaseModel):
    name: Optional[str]
    iteration_target: Optional[int]
    map_target: Optional[float]
    training_dataset_count_target: Optional[int]

    mining_strategy: MiningStrategy = MiningStrategy.chunk
    chunk_size: Optional[int]
    training_dataset_group_id: int
    mining_dataset_id: Optional[int]
    testing_dataset_id: Optional[int]
    description: Optional[str]
    initial_model_id: Optional[int]


class ProjectInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ProjectBase):
    training_dataset_group_id: int
    mining_dataset_id: Optional[int]
    testing_dataset_id: Optional[int]
    initial_model_id: Optional[int]
    current_iteration: Optional[IterationInDBBase]

    class Config:
        orm_mode = True


# Properties to return to caller
class Project(ProjectInDBBase):
    dataset_count: int = 0
    model_count: int = 0
    training_keywords: List[str]
    current_iteration_id: Optional[int]

    @validator("training_keywords", pre=True)
    def unpack_keywords(cls, v: str) -> List[str]:
        return json.loads(v)


class ProjectOut(Common):
    result: Project


class ProjectsOut(Common):
    result: List[Project]


class ProjectPagination(BaseModel):
    total: int
    items: List[Project]


class ProjectPaginationOut(Common):
    result: ProjectPagination
