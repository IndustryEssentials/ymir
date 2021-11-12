from typing import List, Optional

from pydantic import BaseModel

from .common import Common


class KeywordOut(Common):
    result: Optional[List[str]]
