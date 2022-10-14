from typing import Dict, List, Optional
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
    task_id: Optional[int]
    is_finished: Optional[bool]
    state: Optional[ResultState]
    percent: Optional[float]


class IterationStepCreate(BaseModel):
    name: str
    task_type: TaskType
    iteration_id: int


class IterationStepUpdate(BaseModel):
    is_finished: Optional[bool]
    task_id: Optional[int]
    serialized_presetting: str


class IterationStepInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, IterationStepBase):
    percent: Optional[float]
    state: Optional[ResultState]
    presetting: Optional[Dict]

    class Config:
        orm_mode = True


class IterationStep(IterationStepInDBBase):
    pass


class IterationStepOut(Common):
    result: IterationStep


class IterationStepsOut(Common):
    result: List[IterationStep]
