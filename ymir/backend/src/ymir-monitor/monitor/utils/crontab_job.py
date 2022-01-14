import logging
import sys
from typing import Dict

import requests
import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from common_utils.percent_log_util import  PercentLogHandler
from monitor.config import settings
from monitor.libs import redis_handler
from monitor.libs.redis_handler import RedisHandler
from monitor.libs.services import TaskService
from monitor.schemas.task import StorageStructure
from monitor.schemas.task import TaskStorageStructure
from proto.backend_pb2 import TaskState


def send_updated_task(updated_info: Dict[str, TaskStorageStructure]) -> None:
    requests.post(url=f"{settings.POSTMAN_URL}/events/taskstates", json=updated_info)
    logging.info(f"send_updated_task: {updated_info}")


def deal_updated_task(
    redis_client: RedisHandler,
    task_updated: Dict[str, TaskStorageStructure],
    task_id_finished: Dict[str, TaskStorageStructure],
) -> None:
    # sentry will catch Exception
    send_updated_task(task_updated)
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
            runtime_log_content = PercentLogHandler.parse_percent_log(log_path)
            if isinstance(runtime_log_content, str):
                # any sub task's log failed, pass this task
                sentry_sdk.capture_message(runtime_log_content)
                logging.warning(runtime_log_content)
                flag_task_updated = False
                break

            runtime_log_contents[log_path] = runtime_log_content
            if runtime_log_content.timestamp != previous_log_content["timestamp"]:
                flag_task_updated = True

        if flag_task_updated:
            content_merged = TaskService.merge_task_progress_contents(runtime_log_contents)
            if content_merged.state in [
                TaskState.TaskStateDone,
                TaskState.TaskStateError,
            ]:
                task_id_finished.append(task_id)
            task_updated[task_id] = dict(
                raw_log_contents=runtime_log_contents,
                task_extra_info=content["task_extra_info"],
                percent_result=content_merged,
            )

    task_updated = StorageStructure.parse_obj(task_updated).dict()

    if len(task_updated):
        deal_updated_task(redis_client, task_updated, task_id_finished)  # type: ignore


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, format="%(levelname)-8s: [%(asctime)s] %(message)s", level=logging.INFO)
    sentry_sdk.init(settings.MONITOR_SENTRY_DSN)
    sched = BlockingScheduler()
    sched.add_job(monitor_percent_log, "interval", seconds=settings.INTERVAL_SECONDS)
    sched.start()
