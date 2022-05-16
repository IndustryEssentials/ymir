from datetime import datetime
from enum import IntEnum, unique
import logging
from typing import List, Optional

from pydantic import BaseModel


@unique
class LogState(IntEnum):
    UNKNOWN = 0
    PENDING = 1
    RUNNING = 2
    DONE = 3
    ERROR = 4


class PercentResult(BaseModel):
    task_id: str
    timestamp: str
    percent: float
    state: LogState
    state_code: Optional[int] = 0
    state_message: Optional[str] = None
    stack_error_info: Optional[str] = None


class PercentLogHandler:
    @staticmethod
    def parse_percent_log(log_file: str) -> PercentResult:
        with open(log_file, "r") as f:
            monitor_file_lines = f.readlines()
        content_row_one = monitor_file_lines[0].strip().split("\t")
        if not monitor_file_lines or len(content_row_one) < 4:
            raise ValueError(f"invalid percent log file: {log_file}")

        task_id, timestamp, percent, state, *_ = content_row_one
        percent_result = PercentResult(task_id=task_id, timestamp=float(timestamp), percent=percent, state=int(state))
        if len(content_row_one) > 4:
            percent_result.state_code = int(content_row_one[4])
        if len(content_row_one) > 5:
            percent_result.state_message = content_row_one[5]
        if len(monitor_file_lines) > 1:
            percent_result.stack_error_info = "\n".join(monitor_file_lines[1:100])

        return percent_result

    @staticmethod
    def write_percent_log(log_file: str,
                          tid: str,
                          percent: float,
                          state: LogState,
                          error_code: int = None,
                          error_message: str = None,
                          msg: str = None) -> None:
        if not log_file:
            raise RuntimeError("Invalid log_file")
        content_list: List[str] = [tid, f"{datetime.now().timestamp():.6f}", str(percent), str(state.value)]
        if error_code and error_message:
            content_list.extend([str(int(error_code)), error_message])
        content = '\t'.join(content_list)
        if msg:
            content = '\n'.join([content, msg])
        with open(log_file, 'w') as f:
            logging.info(f"writing task info to {log_file}\n{content}")
            f.write(content)
        return
