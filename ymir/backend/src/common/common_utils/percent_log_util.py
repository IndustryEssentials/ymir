from typing import Optional

from pydantic import BaseModel

from proto import backend_pb2


class PercentResult(BaseModel):
    task_id: str
    timestamp: str
    percent: float
    state: int
    state_code: Optional[int] = 0
    state_message: Optional[str] = None
    stack_error_info: Optional[str] = None


class PercentLogHandler:
    @staticmethod
    def task_state_str_to_code(state: str) -> backend_pb2.TaskState:
        _task_state_to_enum = {
            "pending": backend_pb2.TaskState.TaskStatePending,
            "running": backend_pb2.TaskState.TaskStateRunning,
            "runing": backend_pb2.TaskState.TaskStateRunning,
            "done": backend_pb2.TaskState.TaskStateDone,
            "error": backend_pb2.TaskState.TaskStateError,
        }
        return _task_state_to_enum[state]

    @staticmethod
    def parse_percent_log(log_file: str) -> PercentResult:
        with open(log_file, "r") as f:
            monitor_file_lines = f.readlines()
        content_row_one = monitor_file_lines[0].strip().split("\t")
        if not monitor_file_lines or len(content_row_one) < 4:
            raise ValueError(f"invalid percent log file: {log_file}")

        task_id, timestamp, percent, tmp_state, *_ = content_row_one
        state = PercentLogHandler.task_state_str_to_code(tmp_state)
        percent_result = PercentResult(task_id=task_id, timestamp=int(timestamp), percent=percent, state=state)
        if len(content_row_one) > 4:
            percent_result.state_code = int(content_row_one[4])
        if len(content_row_one) > 5:
            percent_result.state_message = content_row_one[5]
        if len(monitor_file_lines) > 1:
            percent_result.stack_error_info = "\n".join(monitor_file_lines[1:100])

        return percent_result
