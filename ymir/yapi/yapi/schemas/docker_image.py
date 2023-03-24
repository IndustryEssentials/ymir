from typing import Dict, List, Optional

from pydantic import BaseModel
from yapi.constants.state import ObjectType, DockerImageType, DockerImageState
from yapi.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
)


class DockerImageBase(BaseModel):
    pass


class DockerImageConfig(BaseModel):
    config: Optional[Dict]
    type: DockerImageType


class DockerImage(IdModelMixin, DateTimeModelMixin, DockerImageBase):
    url: str
    state: DockerImageState
    object_type: ObjectType
    configs: List[DockerImageConfig]


class DockerImagePagination(BaseModel):
    total: int
    items: List[DockerImage]


class DockerImagePaginationOut(Common):
    result: DockerImagePagination


class DockerImageOut(Common):
    result: DockerImage


class DockerImagesOut(Common):
    result: List[DockerImage]
