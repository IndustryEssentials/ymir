import json

from pydantic import BaseModel, Field, root_validator
from typing import Any, Dict, List, Optional

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class ModelStageBase(BaseModel):
    name: str = Field(description="Model stage Name")
    map: Optional[float] = Field(description="Mean Average Precision")
    metrics: Optional[Dict]
    timestamp: int = Field(description="Timestamp")
    model_id: int


class ModelStageCreate(ModelStageBase):
    serialized_metrics: Optional[str] = None

    @root_validator(pre=True)
    def process_metrics(cls, values: Any) -> Any:
        if values.get("metrics"):
            values["map"] = values["metrics"]["ap"]
            values["serialized_metrics"] = json.dumps(values["metrics"])
        return values


class ModelStageUpdate(ModelStageBase):
    pass


class ModelStageInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ModelStageBase):
    class Config:
        orm_mode = True


class Model(BaseModel):
    """
    Just a replica of model schema, to avoid circular import
    """

    id: int
    hash: str
    group_name: str
    version_num: int

    class Config:
        orm_mode = True


class ModelStage(ModelStageInDBBase):
    model: Model


class ModelStageOut(Common):
    result: ModelStage


class ModelStagesOut(Common):
    result: List[ModelStage]
