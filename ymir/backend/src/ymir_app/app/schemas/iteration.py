from typing import List, Optional, Union, Dict
from pydantic import BaseModel

from app.constants.state import IterationStage, ResultState, TaskType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    DatasetResult,
    ModelResult,
    IdModelMixin,
    IsDeletedModelMixin,
)


class IterationBase(BaseModel):
    iteration_round: int
    previous_iteration: int
    description: Optional[str]
    current_stage: Optional[IterationStage]
    mining_dataset_id: Optional[int]
    mining_input_dataset_id: Optional[int]
    mining_output_dataset_id: Optional[int]
    label_output_dataset_id: Optional[int]
    training_input_dataset_id: Optional[int]
    training_output_model_id: Optional[int]
    training_output_model_stage_id: Optional[int]
    validation_dataset_id: Optional[int]
    user_id: int
    project_id: int


# Sufficient properties to create a iteration
class IterationCreate(BaseModel):
    iteration_round: int
    previous_iteration: int
    description: Optional[str]
    project_id: int
    current_stage: Optional[IterationStage] = IterationStage.prepare_mining
    mining_dataset_id: Optional[int]
    mining_input_dataset_id: Optional[int]
    mining_output_dataset_id: Optional[int]
    label_output_dataset_id: Optional[int]
    training_input_dataset_id: Optional[int]
    training_output_model_id: Optional[int]
    training_output_model_stage_id: Optional[int]
    validation_dataset_id: Optional[int]


# Properties that can be changed
class IterationUpdate(BaseModel):
    current_stage: Optional[IterationStage]
    description: Optional[str]
    mining_input_dataset_id: Optional[int]
    mining_output_dataset_id: Optional[int]
    label_output_dataset_id: Optional[int]
    training_input_dataset_id: Optional[int]
    training_output_model_id: Optional[int]
    training_output_model_stage_id: Optional[int]
    validation_dataset_id: Optional[int]

    class Config:
        use_enum_values = True


class IterationStepLite(BaseModel):
    """
    Copied from iteration_step, to avoid circular importing
    """

    id: int
    name: str
    task_type: TaskType
    task_id: Optional[int]
    is_finished: Optional[bool]
    state: Optional[ResultState]
    percent: Optional[float]
    presetting: Optional[Dict]
    result: Union[DatasetResult, ModelResult, None]

    class Config:
        orm_mode = True


class IterationInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, IterationBase):
    current_step: Optional[IterationStepLite]
    iteration_steps: List[IterationStepLite]

    class Config:
        orm_mode = True


# Properties to return to caller
class Iteration(IterationInDBBase):
    pass


class IterationOut(Common):
    result: Iteration


class IterationsOut(Common):
    result: List[Iteration]


class IterationPagination(BaseModel):
    total: int
    items: List[Iteration]


class IterationPaginationOut(Common):
    result: IterationPagination


class MiningRatio(BaseModel):
    class_name: Optional[str]
    processed_assets_count: int
    total_assets_count: int


class IterationMiningProgress(BaseModel):
    total_mining_ratio: MiningRatio
    class_wise_mining_ratio: List[MiningRatio]
    negative_ratio: MiningRatio


class IterationMiningProgressOut(Common):
    result: IterationMiningProgress
