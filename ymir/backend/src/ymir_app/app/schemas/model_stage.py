from pydantic import Field
from typing import Optional

from app.schemas.common import IdModelMixin


class ModelStageBase(IdModelMixin):
    name: str = Field(description="Model stage Name")
    is_best: bool = Field(description="Is best stage")
    map: Optional[float] = Field(description="Mean Average Precision")
    timestamp: int = Field(description="Timestamp")

    class Config:
        orm_mode = True
