from enum import IntEnum
from typing import Dict, List, Optional

from pydantic import BaseModel

from common_utils.task_state_schema import TaskStateEnum


class MonitorType(IntEnum):
    PERCENT = 1


class TaskParameter(BaseModel):
    task_id: str
    user_id: str
    monitor_type: MonitorType = MonitorType.PERCENT
    log_paths: List[str]
    description: Optional[str]


class PercentResult(BaseModel):
    task_id: str
    timestamp: str
    percent: float
    state: TaskStateEnum
    state_code: int = 0
    state_message: Optional[str] = None
    stack_error_info: Optional[str] = None


class TaskExtraInfo(BaseModel):
    user_id: Optional[str] = None
    monitor_type: MonitorType = MonitorType.PERCENT
    log_paths: List[str]
    description: Optional[str]


class TaskStorageStructure(BaseModel):
    raw_log_contents: Dict[str, PercentResult]
    task_extra_info: TaskExtraInfo
    percent_result: PercentResult


class StorageStructure(BaseModel):
    __root__: Dict[str, TaskStorageStructure]

    def dict(self) -> Dict:  # type: ignore
        return super().dict()["__root__"]
