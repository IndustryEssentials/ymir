from typing import Dict, List, Optional, Union
from pydantic import BaseModel

from app.constants.state import TaskType, ResultState
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    DatasetResult,
    ModelResult,
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
    serialized_presetting: Optional[str]

    class Config:
        use_enum_values = True


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
    result: Union[ModelResult, DatasetResult, None]


class IterationStepOut(Common):
    result: IterationStep


class IterationStepsOut(Common):
    result: List[IterationStep]
