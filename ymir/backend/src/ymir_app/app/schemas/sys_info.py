from pydantic import BaseModel

from app.schemas.common import Common


class SysInfoBase(BaseModel):
    gpu_count: int
    openpai_enabled: bool


class SysInfo(SysInfoBase):
    pass


class SysInfoOut(Common):
    result: SysInfo
