from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field, validator


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


class OperationAction(str, Enum):
    hide = "hide"
    unhide = "unhide"


class Operation(BaseModel):
    action: OperationAction = Field(example="hide")
    id_: int = Field(alias="id")


class BatchOperations(BaseModel):
    project_id: int
    operations: List[Operation]

