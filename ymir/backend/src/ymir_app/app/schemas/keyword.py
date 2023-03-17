from typing import List, Optional

from pydantic import BaseModel, validator

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


class KeywordsInput(Common):
    keywords: List[SingleLabel]

    @validator("keywords")
    def dedup(cls, v: List[SingleLabel]) -> List[SingleLabel]:
        uniq = []
        for label in v:
            if label not in uniq:
                uniq.append(label)
        return uniq


class KeywordsCheckDupOut(Common):
    result: List[str]
