from typing import List, Optional

from pydantic import BaseModel

from app.constants.state import IterationStage
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class IterationBase(BaseModel):
    iteration_round: int
    description: Optional[str]
    current_stage: Optional[IterationStage]
    mining_input_dataset_id: Optional[int]
    mining_output_dataset_id: Optional[int]
    label_output_dataset_id: Optional[int]
    training_input_dataset_id: Optional[int]
    training_output_model_id: Optional[int]
    user_id: int
    project_id: int


# Sufficient properties to create a iteration
class IterationCreate(IterationBase):
    pass


# Properties that can be changed
class IterationUpdate(BaseModel):
    current_stage: IterationStage
    description: Optional[str]
    mining_input_dataset_id: Optional[int]
    mining_output_dataset_id: Optional[int]
    label_output_dataset_id: Optional[int]
    training_input_dataset_id: Optional[int]
    training_output_model_id: Optional[int]


class IterationInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, IterationBase):
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
