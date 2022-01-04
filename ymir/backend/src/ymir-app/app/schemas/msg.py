from typing import Optional

from pydantic import BaseModel

from .common import Common


class Msg(Common):
    result: Optional[str] = None
