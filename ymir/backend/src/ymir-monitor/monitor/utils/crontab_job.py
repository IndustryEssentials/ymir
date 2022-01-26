import logging
import sys
from typing import List

import requests
import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from common_utils.percent_log_util import PercentLogHandler, PercentResult, LogState
from monitor.config import settings
from monitor.libs import redis_handler
from monitor.libs.redis_handler import RedisHandler
from monitor.libs.services import TaskService
from monitor.schemas.task import TaskSetStorageStructure


def send_updated_task(updated_info: TaskSetStorageStructure) -> None:
    requests.post(url=f"{settings.POSTMAN_URL}/events/taskstates", json=updated_info.dict())
    logging.info(f"send_updated_task: {updated_info.dict()}")


def deal_updated_task(
    redis_client: RedisHandler, task_updated_model: TaskSetStorageStructure, task_id_finished: List[str],
) -> None:
    # sentry will catch Exception
    send_updated_task(task_updated_model)
    task_updated = task_updated_model.dict()
    redis_client.hmset(settings.MONITOR_RUNNING_KEY, mapping=task_updated)
    if task_id_finished:
        redis_client.hmset(
            settings.MONITOR_FINISHED_KEY, mapping={task_id: task_updated[task_id] for task_id in task_id_finished}
        )
        redis_client.hdel(settings.MONITOR_RUNNING_KEY, *task_id_finished)

        logging.info(f"finished task ids {task_id_finished}")


def monitor_percent_log() -> None:
    redis_client = redis_handler.RedisHandler()
    contents = redis_client.hgetall(settings.MONITOR_RUNNING_KEY)

    task_updated = dict()
    task_id_finished = []
    for task_id, content in contents.items():
        flag_task_updated = False
        runtime_log_contents = dict()
        for log_path, previous_log_content in content["raw_log_contents"].items():
            try:
                runtime_log_content = PercentLogHandler.parse_percent_log(log_path)
            except ValueError as e:
                sentry_sdk.capture_exception(e)
                logging.warning(e)
                runtime_log_content = PercentResult(task_id=task_id, timestamp="123", percent=0.0, state=LogState.ERROR)

            runtime_log_contents[log_path] = runtime_log_content
            if runtime_log_content.timestamp != previous_log_content["timestamp"]:
                flag_task_updated = True

        if flag_task_updated:
            content_merged = TaskService.merge_task_progress_contents(runtime_log_contents)
            if content_merged.state in [LogState.DONE, LogState.ERROR]:
                task_id_finished.append(task_id)
            task_updated[task_id] = dict(
                raw_log_contents=runtime_log_contents,
                task_extra_info=content["task_extra_info"],
                percent_result=content_merged,
            )

    if len(task_updated):
        task_updated_model = TaskSetStorageStructure.parse_obj(task_updated)
        deal_updated_task(redis_client, task_updated_model, task_id_finished)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, format="%(levelname)-8s: [%(asctime)s] %(message)s", level=logging.INFO)
    sentry_sdk.init(settings.MONITOR_SENTRY_DSN)
    sched = BlockingScheduler()
    sched.add_job(monitor_percent_log, "interval", seconds=settings.INTERVAL_SECONDS)
    sched.start()
