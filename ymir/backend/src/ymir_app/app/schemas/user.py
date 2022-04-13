from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, validator

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class UserState(IntEnum):
    registered = 1
    active = 2
    declined = 3  # Super Admin refused to activate user
    deactivated = 4  # Super Admin deactivated an active user


class UserRole(IntEnum):
    NORMAL = 1
    ADMIN = 2
    SUPER_ADMIN = 3


# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    avatar: Optional[str] = None
    state: UserState = UserState.registered


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    role: Optional[str] = None


class UserInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, UserBase):
    role: Optional[UserRole] = UserRole.NORMAL

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    hash: Optional[str] = None
    last_login_datetime: Optional[datetime] = None

    @validator("hash", always=True)
    def gen_hash(cls, v: Any, values: Dict) -> str:
        i = values["id"]
        return f"{i:0>4}"


class UserOut(Common):
    result: User


class Users(BaseModel):
    total: int
    items: List[User]


class UsersOut(Common):
    result: Users


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
