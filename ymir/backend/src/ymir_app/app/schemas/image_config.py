import json
from typing import Any, Dict

from pydantic import BaseModel, validator

from app.schemas.common import Common


class ImageConfigBase(BaseModel):
    image_id: int
    config: str
    type: int


class ImageConfigCreate(ImageConfigBase):
    pass


class ImageConfigUpdate(ImageConfigBase):
    pass


class ImageConfigInDB(ImageConfigBase):
    class Config:
        orm_mode = True


class ImageConfig(ImageConfigInDB):
    config: str

    @validator("config")
    def unravel_config(cls, v: str, values: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            return {}
        return json.loads(v)


class ImageConfigOut(Common):
    result: ImageConfig
