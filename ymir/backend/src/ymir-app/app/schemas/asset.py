from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import AnyUrl, BaseModel, Field

from .common import Common


class AssetBase(BaseModel):
    hash: str = Field(description="DocId")
    size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    channel: Optional[int]
    timestamp: Optional[datetime]


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    pass


class Asset(AssetBase):
    url: Union[AnyUrl, str]
    annotations: Optional[List[Dict]]
    metadata: Optional[Dict]
    keywords: Optional[List[str]]


class Assets(BaseModel):
    total: int
    items: List[Asset]
    keywords: Dict[str, int]


class AssetOut(Common):
    result: Union[Asset, Assets]
