from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, validator


class UserRole(IntEnum):
    NORMAL = 1
    ADMIN = 2
    SUPER_ADMIN = 3


class UserInfo(BaseModel):
    id: int
    role: UserRole

    @validator("role", pre=True)
    def default_role(cls, v: Optional[UserRole]) -> UserRole:
        if v is None:
            return UserRole.NORMAL
        return v
