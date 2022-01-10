from enum import Enum, IntEnum
from typing import Dict, List, Optional

from pydantic import BaseModel


class MonitorType(IntEnum):
    PERCENT = 1


class TaskParameter(BaseModel):
    task_id: str
    user_id: str
    monitor_type: MonitorType = MonitorType.PERCENT
    log_path: List[str]
    description: Optional[str]


class TaskStateEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class PercentResult(BaseModel):
    task_id: str
    timestamp: str
    percent: float
    state: TaskStateEnum
    state_code: int = 0
    state_message: str = None
    stack_error_info: str = None


class TaskExtraInfo(BaseModel):
    user_id: str = None
    monitor_type: MonitorType = MonitorType.PERCENT
    log_path: List[str]
    description: Optional[str]


class TaskStorageStructure(BaseModel):
    raw_log_contents: Dict[str, PercentResult]
    task_extra_info: TaskExtraInfo
    percent_result: PercentResult


class StorageStructure(BaseModel):
    __root__: Dict[str, TaskStorageStructure]

    def dict(self):
        return super().dict()["__root__"]


class Test(BaseModel):
    __root__: Optional[Dict[str, str]]
