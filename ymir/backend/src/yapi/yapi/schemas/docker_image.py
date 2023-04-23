from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from yapi.constants.state import ObjectType, DockerImageType, DockerImageState, ResultState
from yapi.schemas.common import Common, DateTimeModelMixin, IdModelMixin


class DockerImageBase(BaseModel):
    pass


class DockerImageConfig(BaseModel):
    config: Optional[Dict]
    object_type: ObjectType
    type: DockerImageType


class DockerImage(IdModelMixin, DateTimeModelMixin, DockerImageBase):
    url: str
    state: DockerImageState = Field(..., deprecated=True)
    result_state: ResultState
    object_type: ObjectType = Field(..., deprecated=True)
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
