from pydantic import BaseModel, Field
from typing import List, Optional

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class ModelStageBase(BaseModel):
    name: str = Field(description="Model stage Name")
    map: Optional[float] = Field(description="Mean Average Precision")
    timestamp: int = Field(description="Timestamp")
    model_id: int


class ModelStageCreate(ModelStageBase):
    pass


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
