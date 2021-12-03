import enum
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class RuntimeType(enum.IntEnum):
    unknown = 0
    training = 1
    mining = 2
    inference = 100


class RuntimeBase(BaseModel):
    name: str
    hash: str
    type: RuntimeType
    config: str


class RuntimeCreate(RuntimeBase):
    ...


class RuntimeUpdate(BaseModel):
    name: str
    hash: str
    config: str


class RuntimeInDBBase(
    IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, RuntimeBase
):
    class Config:
        orm_mode = True


class Runtime(RuntimeInDBBase):
    config: str

    @validator("config")
    def unravel_config(cls, v: str, values: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            return {}
        return json.loads(v)


class RuntimeOut(Common):
    result: Union[Runtime, List[Runtime]]
