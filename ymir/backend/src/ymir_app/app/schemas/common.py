from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.constants.state import MiningStrategy


class Common(BaseModel):
    code: int = 0
    message: str = "success"


class DateTimeModelMixin(BaseModel):
    create_datetime: datetime = None  # type: ignore
    update_datetime: datetime = None  # type: ignore

    @validator("create_datetime", "update_datetime", pre=True)
    def default_datetime(
        cls,
        value: datetime,
    ) -> datetime:  # noqa: N805  # noqa: WPS110
        return value or datetime.now()


class IdModelMixin(BaseModel):
    id: int = Field(alias="id")


class IsDeletedModelMixin(BaseModel):
    is_deleted: bool = False


class IterationContext(BaseModel):
    # data fusion in iteration
    iteration_id: Optional[int]
    exclude_last_result: bool = True
    mining_strategy: MiningStrategy = MiningStrategy.customize
