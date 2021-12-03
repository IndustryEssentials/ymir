from datetime import datetime
from typing import List, Union

from pydantic import BaseModel

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class WorkspaceBase(BaseModel):
    hash: str
    name: str
    user_id: int


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(WorkspaceBase):
    pass


class WorkspaceInDB(
    IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, WorkspaceBase
):
    class Config:
        orm_mode = True


class Workspace(WorkspaceInDB):
    pass


class Workspaces(BaseModel):
    total: int
    items: List[Workspace]


class WorkspaceOut(Common):
    result: Union[Workspace, Workspaces]
