from typing import List, Optional

from pydantic import BaseModel

from app.schemas.common import Common, IdModelMixin
from app.schemas.image import DockerImage


class ImageRelationshipBase(BaseModel):
    src_image_id: int
    dest_image_id: int


class ImageRelationshipCreate(ImageRelationshipBase):
    pass


class ImageRelationshipsCreate(BaseModel):
    dest_image_ids: List[int]


class ImageRelationshipUpdate(ImageRelationshipBase):
    pass


class ImageRelationshipInDB(ImageRelationshipBase):
    class Config:
        orm_mode = True


class ImageRelationship(ImageRelationshipInDB):
    pass


class ImageRelationshipOut(Common):
    result: ImageRelationship


class ImageRelationshipsOut(Common):
    result: List[ImageRelationship]
