from typing import List, Optional

from pydantic import BaseModel

from app.constants.state import DockerImageState
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


class DockerImageCreate(DockerImageBase):
    url: str


class DockerImageLinkCreate(BaseModel):
    docker_image_ids: List[int]


class DockerImageUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_shared: Optional[bool]


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


class DockerImageSharing(BaseModel):
    docker_image_id: int
    contributor: Optional[str]
    organization: Optional[str]
    email: Optional[str]
    phone: Optional[str]


class SharedDockerImageOut(Common):
    result: DockerImageSharing


class DockerImageShared(BaseModel):
    docker_name: Optional[str]
    functions: Optional[str]
    contributor: Optional[str]
    organization: Optional[str]
    description: Optional[str]


class SharedDockerImagesOut(Common):
    result: List[DockerImageShared]
