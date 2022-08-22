from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

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
    url: str
    metadata: Optional[Dict]
    keywords: Optional[List[str]]
    gt: Optional[List[Dict]]
    pred: Optional[List[Dict]]
    cks: Optional[Dict]


class AssetOut(Common):
    result: Asset


class AssetPagination(BaseModel):
    items: List[Asset]
    total: int


class AssetPaginationOut(Common):
    result: AssetPagination
