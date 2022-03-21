from typing import List, Optional

from pydantic import BaseModel

from .common import Common
from common_utils.labels import SingleLabel


class KeywordUpdate(BaseModel):
    aliases: Optional[List[str]]


class KeywordOut(Common):
    result: SingleLabel


class KeywordsCreate(BaseModel):
    keywords: List[SingleLabel]
    dry_run: bool = False


class KeywordsPagination(BaseModel):
    total: int
    items: List[SingleLabel]


class KeywordsPaginationOut(Common):
    result: KeywordsPagination


class KeywordsCreateResult(BaseModel):
    failed: List[str]


class KeywordsCreateOut(Common):
    result: KeywordsCreateResult
