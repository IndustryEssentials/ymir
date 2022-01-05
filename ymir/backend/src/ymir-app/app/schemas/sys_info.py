from typing import List, Optional, Union

from pydantic import BaseModel

from app.schemas.common import Common, IdModelMixin


class SysInfoBase(BaseModel):
    gpu_count: int


class SysInfo(SysInfoBase):
    pass


class SysInfoOut(Common):
    result: SysInfo
