from typing import List, Optional, Union

from pydantic import BaseModel

from app.schemas.common import Common, IdModelMixin


class RoleBase(BaseModel):
    name: Optional[str]
    description: Optional[str]


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleInDBBase(IdModelMixin, RoleBase):
    class Config:
        orm_mode = True


class Role(RoleInDBBase):
    pass


class RoleInDB(RoleInDBBase):
    pass


class RoleOut(Common):
    result: Union[Role, List[Role]]
