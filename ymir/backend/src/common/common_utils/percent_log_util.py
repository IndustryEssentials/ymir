from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel


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
    state_message: Optional[str] = None
    stack_error_info: Optional[str] = None


class PercentLogHandler:
    @staticmethod
    def parse_percent_log(log_file: str) -> Union[PercentResult, str]:
        with open(log_file, "r") as f:
            monitor_file_lines = f.readlines()
        content_row_one = monitor_file_lines[0].strip().split("\t")
        if not monitor_file_lines or len(content_row_one) < 4:
            return f"invalid percent log file: {log_file}"

        task_id, timestamp, percent, state, *_ = content_row_one
        percent_result = PercentResult(task_id=task_id, timestamp=int(timestamp), percent=percent, state=state)
        if len(content_row_one) > 4:
            percent_result.state_code = int(content_row_one[4])
        if len(content_row_one) > 5:
            percent_result.state_message = content_row_one[5]
        if len(monitor_file_lines) > 1:
            percent_result.stack_error_info = "\n".join(monitor_file_lines[1:100])

        return percent_result
