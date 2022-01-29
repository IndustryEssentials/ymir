import logging
from typing import Dict
from typing import List

from common_utils.percent_log_util import PercentLogHandler, LogState
from monitor.config import settings
from monitor.libs.redis_handler import RedisHandler
from monitor.schemas.task import TaskParameter, PercentResult, TaskStorageStructure, TaskExtraInfo
from monitor.utils.errors import DuplicateTaskIDError, LogFileError

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, redis: RedisHandler) -> None:
        self._redis = redis

    def add_single_task(self, task_id: str, task_info: Dict) -> None:
        self._redis.hset(settings.MONITOR_RUNNING_KEY, task_id, task_info)

    def get_raw_log_contents(self, log_paths: List[str]) -> Dict[str, PercentResult]:
        result = dict()
        for one_log_file in log_paths:
            try:
                percent_result = PercentLogHandler.parse_percent_log(one_log_file)
            except ValueError as e:
                raise LogFileError(f"percent log content error {e}")
            result[one_log_file] = percent_result

        return result

    @staticmethod
    def merge_task_progress_contents(task_id: str, raw_log_contents: Dict[str, PercentResult]) -> PercentResult:
        percent = 0.0
        log_files_state_set = set()
        max_timestamp_content = None
        for raw_log_content in raw_log_contents.values():
            log_files_state_set.add(raw_log_content.state)
            percent += raw_log_content.percent
            if not max_timestamp_content:
                max_timestamp_content = raw_log_content
            max_timestamp_content = max(max_timestamp_content, raw_log_content, key=lambda x: int(x.timestamp))

        result = max_timestamp_content.copy()  # type: ignore
        if LogState.ERROR in log_files_state_set:
            result.percent = 1.0
            result.state = LogState.ERROR
        elif len(log_files_state_set) == 1 and LogState.DONE in log_files_state_set:
            result.percent = 1.0
            result.state = LogState.DONE
        elif len(log_files_state_set) == 1 and LogState.PENDING in log_files_state_set:
            result.percent = 0.0
            result.state = LogState.PENDING
        else:
            result.percent = percent / len(raw_log_contents)
            result.state = LogState.RUNNING
        result.task_id = task_id
        return result

    def get_running_task(self) -> Dict[str, Dict]:
        contents = self._redis.hgetall(settings.MONITOR_RUNNING_KEY)
        return contents

    def get_finished_task(self) -> Dict[str, Dict]:
        contents = self._redis.hgetall(settings.MONITOR_FINISHED_KEY)
        return contents

    def check_existence(self, task_id: str) -> bool:
        running_existence = self._redis.hexists(settings.MONITOR_RUNNING_KEY, task_id)
        finished_existence = self._redis.hexists(settings.MONITOR_FINISHED_KEY, task_id)

        return running_existence or finished_existence

    def register_task(self, reg_parameters: TaskParameter) -> None:
        if self.check_existence(reg_parameters.task_id):
            raise DuplicateTaskIDError(f"duplicate task id {reg_parameters.task_id}")

        raw_log_contents = self.get_raw_log_contents(reg_parameters.log_paths)
        if len(raw_log_contents) != len(reg_parameters.log_paths):
            raise LogFileError
        percent_result = self.merge_task_progress_contents(reg_parameters.task_id, raw_log_contents)
        task_extra_info = TaskExtraInfo.parse_obj(reg_parameters.dict())
        percent_result = PercentResult.parse_obj(percent_result.dict())

        task_info = TaskStorageStructure(
            raw_log_contents=raw_log_contents, task_extra_info=task_extra_info, percent_result=percent_result,
        )

        self.add_single_task(reg_parameters.task_id, task_info.dict())

        logger.info(f"register task successful: {task_info.dict()} ")
