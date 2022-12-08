import json
from typing import List, Optional

from pydantic import BaseModel, validator

from app.constants.state import MiningStrategy, TrainingType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)

from app.schemas.iteration import Iteration
from app.schemas.dataset import Dataset
from app.schemas.dataset_group import DatasetGroup


class ProjectBase(BaseModel):
    name: str
    description: Optional[str]

    mining_strategy: MiningStrategy = MiningStrategy.chunk
    chunk_size: Optional[int] = 0

    enable_iteration: Optional[bool] = True
    iteration_target: Optional[int]
    map_target: Optional[float]
    training_dataset_count_target: Optional[int]

    is_example: Optional[bool] = False

    training_type: TrainingType = TrainingType.object_detect
    candidate_training_dataset_id: Optional[int]


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
    training_dataset_group_id: Optional[int]
    training_dataset_count_target: Optional[int]

    mining_strategy: MiningStrategy = MiningStrategy.chunk
    chunk_size: Optional[int]
    mining_dataset_id: Optional[int]
    validation_dataset_id: Optional[int]
    testing_dataset_ids: Optional[str]
    description: Optional[str]
    initial_model_id: Optional[int]
    initial_model_stage_id: Optional[int]
    initial_training_dataset_id: Optional[int]
    candidate_training_dataset_id: Optional[int]

    training_keywords: Optional[List[str]]

    class Config:
        use_enum_values = True
        validate_all = True

    @validator("training_keywords")
    def pack_keywords(cls, v: Optional[List[str]]) -> Optional[str]:
        """
        serialize training keywords for db
        """
        if v is not None:
            return json.dumps(v)
        return v


class ProjectInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ProjectBase):
    training_dataset_group_id: Optional[int]
    mining_dataset_id: Optional[int]
    validation_dataset_id: Optional[int]
    initial_model_id: Optional[int]
    initial_model_stage_id: Optional[int]
    initial_training_dataset_id: Optional[int]

    current_iteration: Optional[Iteration]
    training_dataset_group: Optional[DatasetGroup]
    validation_dataset: Optional[Dataset]
    mining_dataset: Optional[Dataset]

    referenced_model_ids: List[int]
    referenced_dataset_ids: List[int]
    testing_dataset_ids: Optional[str]

    class Config:
        orm_mode = True


# Properties to return to caller
class Project(ProjectInDBBase):
    dataset_count: int = 0
    processing_dataset_count: int = 0
    error_dataset_count: int = 0
    model_count: int = 0
    processing_model_count: int = 0
    error_model_count: int = 0
    training_keywords: List[str]
    current_iteration_id: Optional[int]
    total_asset_count: int = 0
    running_task_count: int = 0
    total_task_count: int = 0

    @validator("training_keywords", pre=True)
    def unpack_keywords(cls, v: str) -> List[str]:
        return json.loads(v)

    @validator("enable_iteration", pre=True)
    def make_up_default_value(cls, v: Optional[bool]) -> bool:
        if v is None:
            return True
        return v


class ProjectOut(Common):
    result: Project


class ProjectsOut(Common):
    result: List[Project]


class ProjectPagination(BaseModel):
    total: int
    items: List[Project]


class ProjectPaginationOut(Common):
    result: ProjectPagination


class ProjectStatus(BaseModel):
    is_dirty: bool


class ProjectStatusOut(Common):
    result: ProjectStatus
