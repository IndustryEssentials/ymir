from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field, root_validator, validator

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_admin: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, UserBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    hash: Optional[str] = None

    @validator("hash", always=True)
    def gen_hash(cls, v: Any, values: Dict) -> str:
        i = values["id"]
        return f"{i:0>4}"


class UserOut(Common):
    result: User


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
