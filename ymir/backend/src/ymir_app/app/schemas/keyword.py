from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .common import Common


class KeywordBase(BaseModel):
    name: str
    aliases: Optional[List[str]]
    create_time: datetime = None  # type: ignore
    update_time: datetime = None  # type: ignore


class Keyword(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    aliases: Optional[List[str]]


class KeywordOut(Common):
    result: Keyword


class KeywordsCreate(BaseModel):
    keywords: List[Keyword]
    dry_run: bool = False


class KeywordsPagination(BaseModel):
    total: int
    items: List[Keyword]


class KeywordsPaginationOut(Common):
    result: KeywordsPagination


class KeywordsCreateResult(BaseModel):
    failed: List[str]


class KeywordsCreateOut(Common):
    result: KeywordsCreateResult
