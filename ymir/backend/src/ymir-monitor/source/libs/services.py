import logging
from typing import Dict
from typing import List

from source.config import settings
from source.libs.redis_handler import RedisHandler
from source.schemas.task import TaskParameter, PercentResult, TaskStorageStructure, TaskExtraInfo
from source.utils.errors import DuplicateTaskIDError, LogFileError

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, redis: RedisHandler) -> None:
        self._redis = redis

    @staticmethod
    def parse_percent_log(log_file: str) -> PercentResult:
        with open(log_file, "r") as f:
            monitor_file_lines = f.readlines()
        content_row_one = monitor_file_lines[0].strip().split("\t")
        if not monitor_file_lines or len(content_row_one) < 4:
            logger.error(f"invalid monitor file: {log_file}")
            raise LogFileError

        task_id, timestamp, percent, state, *_ = content_row_one
        percent_result = PercentResult(task_id=task_id, timestamp=int(timestamp), percent=percent, state=state)
        if len(content_row_one) > 4:
            percent_result.state_code = int(content_row_one[4])
        if len(content_row_one) > 5:
            percent_result.state_message = content_row_one[5]
        if len(monitor_file_lines) > 1:
            percent_result.stack_error_info = "\n".join(monitor_file_lines[1:100])

        return percent_result

    def add_single_task(self, task_id: str, percent_result: Dict) -> None:
        self._redis.hset(settings.MONITOR_RUNNING_KEY, task_id, percent_result)

    def get_raw_log_contents(self, log_paths: List[str]) -> Dict[str, PercentResult]:
        result = dict()
        for one_log_file in log_paths:
            result[one_log_file] = self.parse_percent_log(one_log_file)

        return result

    @staticmethod
    def merge_task_progress_contents(raw_log_contents: Dict[str, PercentResult]) -> PercentResult:
        percent = 0.0
        max_timestamp_content = None
        for raw_log_content in raw_log_contents.values():
            # any raw log error, means total task is error
            if raw_log_content.state == "error":
                return raw_log_content

            percent += raw_log_content.percent
            if not max_timestamp_content:
                max_timestamp_content = raw_log_content
            max_timestamp_content = max(max_timestamp_content, raw_log_content, key=lambda x: int(x.timestamp))
        result = max_timestamp_content.copy()  # type: ignore
        result.percent = percent / len(raw_log_contents)

        return result

    def get_running_task(self) -> Dict[str, TaskStorageStructure]:
        contents = self._redis.hgetall(settings.MONITOR_RUNNING_KEY)
        return contents

    def get_finished_task(self) -> Dict[str, TaskStorageStructure]:
        contents = self._redis.hgetall(settings.MONITOR_FINISHED_KEY)
        return contents

    def check_existence(self, task_id: str) -> bool:
        running_existence = self._redis.hexists(settings.MONITOR_RUNNING_KEY, task_id)
        finished_existence = self._redis.hexists(settings.MONITOR_FINISHED_KEY, task_id)

        return running_existence or finished_existence

    def register_task(self, reg_parameters: TaskParameter) -> None:
        if self.check_existence(reg_parameters.task_id):
            raise DuplicateTaskIDError

        raw_log_contents = self.get_raw_log_contents(reg_parameters.log_paths)
        percent_result = self.merge_task_progress_contents(raw_log_contents)
        task_extra_info = TaskExtraInfo.parse_obj(reg_parameters.dict())
        percent_result = PercentResult.parse_obj(percent_result.dict())

        task_info = TaskStorageStructure(
            raw_log_contents=raw_log_contents, task_extra_info=task_extra_info, percent_result=percent_result,
        )

        self.add_single_task(reg_parameters.task_id, task_info.dict())

        logger.info(f"register task successful: {task_info.dict()} ")
