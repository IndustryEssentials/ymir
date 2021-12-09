from typing import Optional

from pydantic import BaseModel

from app.schemas.common import IdModelMixin
from app.schemas.role import Role


class UserRoleBase(BaseModel):
    user_id: Optional[int]
    role_id: Optional[int]


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(UserRoleBase):
    pass


class UserRoleInDBBase(IdModelMixin, UserRoleBase):
    role: Role

    class Config:
        orm_mode = True


class UserRole(UserRoleInDBBase):
    pass


class UserRoleInDB(UserRoleInDBBase):
    pass
