from typing import List, Optional
from pydantic import BaseModel

from app.constants.state import TaskType, ResultState
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class IterationStepBase(BaseModel):
    name: str
    task_type: TaskType
    iteration_id: int
    is_finished: Optional[bool]
    task_id: Optional[int]
    input_dataset_id: Optional[int]
    output_dataset_id: Optional[int]
    output_model_id: Optional[int]
    state: Optional[ResultState]
    percent: Optional[float]


class IterationStepCreate(BaseModel):
    name: str
    task_type: TaskType
    iteration_id: int


class IterationStepUpdate(BaseModel):
    is_finished: Optional[bool]
    task_id: Optional[int]
    input_dataset_id: Optional[int]
    output_dataset_id: Optional[int]
    output_model_id: Optional[int]


class IterationStepInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, IterationStepBase):
    percent: Optional[float]
    state: Optional[ResultState]

    class Config:
        orm_mode = True


class IterationStep(IterationStepInDBBase):
    pass


class IterationStepOut(Common):
    result: IterationStep


class IterationStepsOut(Common):
    result: List[IterationStep]
