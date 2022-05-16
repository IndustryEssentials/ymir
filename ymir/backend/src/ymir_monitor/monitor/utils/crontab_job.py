from datetime import datetime
import json
import logging
import sys
from typing import List

import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from common_utils.percent_log_util import PercentLogHandler, PercentResult, LogState
from id_definition.error_codes import MonitorErrorCode
from monitor.config import settings
from monitor.libs import redis_handler
from monitor.libs.redis_handler import RedisHandler
from monitor.libs.services import TaskService
from monitor.schemas.task import TaskSetStorageStructure


def send_updated_task(redis_client: RedisHandler, updated_info: TaskSetStorageStructure) -> None:
    for event in updated_info.dict().values():
        logging.info("send_updated_task: %s to redis stream", event)
        redis_client.xadd(settings.APP_REDIS_STREAM, {"payload": json.dumps(event)})


def process_updated_task(
    redis_client: RedisHandler,
    task_updated_model: TaskSetStorageStructure,
    task_id_finished: List[str],
) -> None:
    # sentry will catch Exception
    send_updated_task(redis_client, task_updated_model)
    task_updated = task_updated_model.dict()
    redis_client.hmset(settings.MONITOR_RUNNING_KEY, mapping=task_updated)
    if task_id_finished:
        redis_client.hmset(
            settings.MONITOR_FINISHED_KEY, mapping={task_id: task_updated[task_id] for task_id in task_id_finished}
        )
        redis_client.hdel(settings.MONITOR_RUNNING_KEY, *task_id_finished)

        logging.info(f"finished task ids {task_id_finished}")


def update_monitor_percent_log() -> None:
    redis_client = redis_handler.RedisHandler()
    contents = redis_client.hgetall(settings.MONITOR_RUNNING_KEY)

    task_updated = dict()
    task_id_finished = []
    for task_id, content in contents.items():
        flag_task_updated = False
        runtime_log_contents = dict()
        logging.info(f"content: {content}")
        for log_path, previous_log_content in content["raw_log_contents"].items():
            try:
                runtime_log_content = PercentLogHandler.parse_percent_log(log_path)
            except ValueError as e:
                sentry_sdk.capture_exception(e)
                logging.exception(e)
                runtime_log_content = PercentResult(task_id=task_id,
                                                    timestamp=f"{datetime.now().timestamp():.6f}",
                                                    percent=1.0,
                                                    state=LogState.ERROR,
                                                    state_code=MonitorErrorCode.PERCENT_LOG_PARSE_ERROR,
                                                    state_message=f"logfile parse error: {log_path}")

            runtime_log_contents[log_path] = runtime_log_content
            if runtime_log_content.timestamp != previous_log_content["timestamp"]:
                flag_task_updated = True

        if flag_task_updated:
            task_extra_info = content["task_extra_info"]
            content_merged = TaskService.merge_task_progress_contents(
                task_id=task_id,
                raw_log_contents=runtime_log_contents,
                log_path_weights=task_extra_info["log_path_weights"],
            )
            if content_merged.state in [LogState.DONE, LogState.ERROR]:
                task_id_finished.append(task_id)
            task_updated[task_id] = dict(
                raw_log_contents=runtime_log_contents,
                task_extra_info=task_extra_info,
                percent_result=content_merged,
            )

    if len(task_updated):
        task_updated_model = TaskSetStorageStructure.parse_obj(task_updated)
        process_updated_task(redis_client, task_updated_model, task_id_finished)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, format="%(levelname)-8s: [%(asctime)s] %(message)s", level=logging.INFO)
    sentry_sdk.init(settings.MONITOR_SENTRY_DSN)
    sched = BlockingScheduler()
    sched.add_job(update_monitor_percent_log, "interval", seconds=settings.INTERVAL_SECONDS)
    sched.start()
