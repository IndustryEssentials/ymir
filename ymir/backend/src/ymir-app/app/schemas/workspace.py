from typing import Any, Optional

from pydantic import BaseModel, root_validator

from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class WorkspaceBase(BaseModel):
    user_id: int
    hash: Optional[str] = None
    name: Optional[str] = None

    @root_validator
    def default_hash(cls, values: Any) -> Any:
        """
        For now, for each user there is only one workspace
        simply using `user_id` to generate default `hash` and `name`
        """
        user_id = values["user_id"]
        hash_ = f"{user_id:0>6}"
        values["hash"] = values["hash"] or hash_
        values["name"] = values["name"] or hash_
        return values


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


class WorkspaceOut(Common):
    result: Workspace
