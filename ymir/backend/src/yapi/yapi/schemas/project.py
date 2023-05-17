from typing import Any, List, Optional

from pydantic import BaseModel, root_validator
from yapi.constants.state import ObjectType
from yapi.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    generate_uuid,
)


class ProjectBase(BaseModel):
    object_type: ObjectType


class ProjectCreate(ProjectBase):
    pass


class AppProjectCreate(ProjectCreate):
    name: Optional[str]
    training_keywords: List = []

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        values["name"] = values.get("name") or generate_uuid()
        return values


class Project(IdModelMixin, DateTimeModelMixin, ProjectBase):
    pass


class ProjectPagination(BaseModel):
    total: int
    items: List[Project]


class ProjectPaginationOut(Common):
    result: ProjectPagination


class ProjectOut(Common):
    result: Project
