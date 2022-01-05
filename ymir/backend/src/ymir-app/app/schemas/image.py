import enum
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator

from app.constants.state import DockerImageState, DockerImageType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)


class DockerImageBase(BaseModel):
    name: str
    type: Optional[DockerImageType] = DockerImageType.unknown
    state: Optional[DockerImageState] = DockerImageState.pending
    hash: Optional[str]
    url: Optional[str]
    config: Optional[str]
    description: Optional[str]


class DockerImageCreate(DockerImageBase):
    pass


class DockerImageLinkCreate(BaseModel):
    docker_image_ids: List[int]


class DockerImageUpdate(BaseModel):
    name: Optional[str]
    config: Optional[str]
    description: Optional[str]
    is_shared: Optional[bool]


class DockerImageUpdateConfig(DockerImageUpdate):
    hash: Optional[str]
    type: Optional[int]
    state: Optional[int]


class DockerImageInDBBase(
    IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, DockerImageBase
):
    hash: Optional[str]
    config: Optional[str]
    state: DockerImageState = DockerImageState.pending

    class Config:
        orm_mode = True


class DockerImageInDB(DockerImageInDBBase):
    config: Optional[str]

    @validator("config")
    def unravel_config(cls, v: str, values: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            return {}
        return json.loads(v)


class DockerImage(DockerImageInDB):
    related: List[DockerImageInDB]


class DockerImages(BaseModel):
    total: int
    items: List[DockerImage]


class DockerImagesOut(Common):
    result: DockerImages


class DockerImageOut(Common):
    result: DockerImage


class DockerImageSharing(BaseModel):
    submitter: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    organization: Optional[str]
