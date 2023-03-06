import json
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.constants.state import ResultState, TaskType, ObjectType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.task import TaskInternal


class PredictionBase(BaseModel):
    name: str
    hash: str = Field(description="related task hash")
    description: Optional[str]
    user_id: int
    project_id: int
    task_id: int
    dataset_id: int
    model_id: int
    model_stage_id: int
    source: TaskType = TaskType.dataset_infer
    result_state: ResultState = ResultState.processing
    asset_count: Optional[int]
    keyword_count: Optional[int]
    keywords: Optional[str]

    class Config:
        use_enum_values = True
        validate_all = True


class PredictionCreate(PredictionBase):
    class Config:
        use_enum_values = True


class PredictionUpdate(BaseModel):
    description: Optional[str]
    result_state: Optional[ResultState]
    keywords: Optional[str]
    asset_count: Optional[int]
    keyword_count: Optional[int]


class PredictionInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, PredictionBase):
    related_task: Optional[TaskInternal]
    object_type: Optional[ObjectType] = ObjectType.object_detect
    is_visible: bool

    class Config:
        orm_mode = True


class Prediction(PredictionInDBBase):
    keywords: Optional[str]

    # make sure all the json dumped value is unpacked before returning to caller
    @validator("keywords")
    def unpack(cls, v: Optional[str]) -> Dict[str, int]:
        if v is None:
            return {}
        return json.loads(v)


class PredictionPagination(BaseModel):
    total: int
    items: Dict[int, List[Prediction]]


class PredictionPaginationOut(Common):
    result: PredictionPagination


class PredictionOut(Common):
    result: Prediction


class PredictionsOut(Common):
    result: List[Prediction]


class PredictionEvaluationCreate(BaseModel):
    project_id: int
    prediction_ids: List[int]
    confidence_threshold: Optional[float] = None
    iou_threshold: Optional[float] = None
    require_average_iou: bool = False
    need_pr_curve: bool = False
    main_ck: Optional[str] = None


class PredictionEvaluationOut(Common):
    # dict of prediction_id to evaluation result
    result: Dict[int, Optional[Dict]]
