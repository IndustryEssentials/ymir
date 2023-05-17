from typing import List, Optional

from pydantic import BaseModel

from app.constants.state import DockerImageState, ObjectType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.image_config import ImageConfig


class DockerImageBase(BaseModel):
    name: str
    state: Optional[DockerImageState] = DockerImageState.pending
    hash: Optional[str]
    url: Optional[str]
    description: Optional[str]
    enable_livecode: Optional[bool] = False
    object_type: Optional[int] = ObjectType.unknown


class DockerImageCreate(DockerImageBase):
    url: str


class DockerImageLinkCreate(BaseModel):
    docker_image_ids: List[int]


class DockerImageUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_shared: Optional[bool]
    enable_livecode: Optional[bool]
    object_type: Optional[int]


class DockerImageInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, DockerImageBase):
    hash: Optional[str]
    state: DockerImageState = DockerImageState.pending
    is_shared: Optional[bool]

    class Config:
        orm_mode = True


class DockerImageInDB(DockerImageInDBBase):
    pass


class DockerImage(DockerImageInDB):
    related: List[DockerImageInDB]
    configs: List[ImageConfig]


class DockerImages(BaseModel):
    total: int
    items: List[DockerImage]


class DockerImagesOut(Common):
    result: DockerImages


class DockerImageOut(Common):
    result: DockerImage
