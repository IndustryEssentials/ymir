import itertools
import logging
import sys
import time
from typing import List, Optional

import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from common_utils.percent_log_util import PercentLogHandler, PercentResult, LogState
from id_definition.error_codes import MonitorErrorCode
from monitor.config import settings
from monitor.libs import redis_handler
from monitor.libs.redis_handler import RedisHandler
from monitor.libs.services import TaskService
from monitor.schemas.task import TaskStorageStructure


def notify_updated_task(redis_client: RedisHandler, task_infos: List[TaskStorageStructure]) -> None:
    """
    Enqueue updated task to Redis Stream.
    Ymir App will fetch and pass them to Frontend.
    """
    for task_info in task_infos:
        logging.info("notify_updated_task: %s to redis stream", task_info.percent_result)
        redis_client.xadd(settings.APP_REDIS_STREAM, {"payload": task_info.json()})


def _update_redis_for_running_tasks(redis_client: RedisHandler, task_infos: List[TaskStorageStructure]) -> None:
    # sentry will catch Exception
    if not task_infos:
        return
    task_info_mapping = {task_info.percent_result.task_id: task_info.dict() for task_info in task_infos}
    redis_client.hmset(settings.MONITOR_RUNNING_KEY, mapping=task_info_mapping)
    logging.info(f"processed redis key for updated task ids {task_info_mapping.keys()}")


def _update_redis_for_finished_tasks(redis_client: RedisHandler, task_infos: List[TaskStorageStructure]) -> None:
    if not task_infos:
        return
    task_info_mapping = {task_info.percent_result.task_id: task_info.dict() for task_info in task_infos}
    redis_client.hmset(settings.MONITOR_FINISHED_KEY, mapping=task_info_mapping)
    redis_client.hdel(settings.MONITOR_RUNNING_KEY, *task_info_mapping.keys())
    logging.info(f"processed redis key for finished task ids {task_info_mapping.keys()}")


def update_monitor_redis(redis_client: RedisHandler, task_infos: List[TaskStorageStructure]) -> None:
    for state, tasks in itertools.groupby(
        sorted(task_infos, key=lambda x: x.percent_result.state), key=lambda x: x.percent_result.state
    ):
        # group tasks by states so as to bulk process tasks in the same state in one go
        if state in [LogState.DONE, LogState.ERROR]:
            _update_redis_for_finished_tasks(redis_client, list(tasks))
        else:
            _update_redis_for_running_tasks(redis_client, list(tasks))


def read_latest_log(log_path: str, task_id: str) -> Optional[PercentResult]:
    try:
        percent_result = PercentLogHandler.parse_percent_log(log_path)
    except EOFError:
        msg = f"skip empty log file: {log_path}"
        sentry_sdk.capture_exception()
        logging.exception(msg)
        return None
    except Exception:
        msg = f"failed to parse log file: {log_path}"
        sentry_sdk.capture_exception()
        logging.exception(msg)
        percent_result = PercentResult(
            task_id=task_id,
            timestamp=f"{time.time():.6f}",
            percent=1.0,
            state=LogState.ERROR,
            state_code=MonitorErrorCode.PERCENT_LOG_PARSE_ERROR,
            state_message=msg,
        )
    return percent_result


def monitor_task_logs() -> None:
    """
    Periodically monitor task logs.
    Only registered tasks will be checked.
    """
    redis_client = redis_handler.RedisHandler()
    running_tasks = redis_client.hgetall(settings.MONITOR_RUNNING_KEY)

    updated_tasks = []
    for task_id, task_info in running_tasks.items():
        # task_info: TaskStorageStructure.dict()
        is_updated_task = False
        raw_log_contents = {}
        logging.info(f"previous percent_result: {task_info['percent_result']}")
        for log_path, previous_percent_result in task_info["raw_log_contents"].items():
            percent_result = read_latest_log(log_path, task_id)
            if not percent_result:
                continue
            logging.info(f"current percent_result: {percent_result}")
            raw_log_contents[log_path] = percent_result
            if percent_result.timestamp != previous_percent_result["timestamp"]:
                is_updated_task = True

        if is_updated_task:
            task_extra_info = task_info["task_extra_info"]
            merged_percent_result = TaskService.merge_task_progress_contents(
                task_id=task_id,
                raw_log_contents=raw_log_contents,
                log_path_weights=task_extra_info["log_path_weights"],
            )
            logging.info(f"merged percent_result: {merged_percent_result}")
            updated_tasks.append(
                TaskStorageStructure(
                    raw_log_contents=raw_log_contents,
                    task_extra_info=task_extra_info,
                    percent_result=merged_percent_result,
                )
            )

    notify_updated_task(redis_client, updated_tasks)
    update_monitor_redis(redis_client, updated_tasks)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, format="%(levelname)-8s: [%(asctime)s] %(message)s", level=logging.INFO)
    sentry_sdk.init(settings.MONITOR_SENTRY_DSN)
    sched = BlockingScheduler()
    sched.add_job(monitor_task_logs, "interval", seconds=settings.INTERVAL_SECONDS)
    sched.start()
