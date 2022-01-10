from apscheduler.schedulers.blocking import BlockingScheduler
from source.libs import redis_handler
from source.config import settings
from source.schemas.task import TaskStateEnum, TaskStorageStructure, StorageStructure
from source.libs.services import TaskService
from source.libs.app_logger import logger
import requests


def send_updated_task(updated_info):
    # if True:
    #     requests.post(
    #         url=settings.DESTINATION_URL,
    #         json=updated_info
    #     )
    logger.info(f"send_updated_task: {updated_info}")


def deal_updated_task(redis_client, task_updated, task_finished):
    print(task_updated)
    send_updated_task(task_updated)
    redis_client.hmset(settings.MONITOR_RUNNING_KEY, mapping=task_updated)

    if task_finished:
        redis_client.hmset(
            settings.MONITOR_FINISHED_KEY, mapping={task_id: task_updated[task_id] for task_id in task_finished}
        )
        redis_client.hdel(settings.MONITOR_RUNNING_KEY, *task_finished)

        logger.info(f"finished task ids {task_finished}")


def monitor_percent_log():
    redis_client = redis_handler.RedisHandler()
    contents = redis_client.hgetall(settings.MONITOR_RUNNING_KEY)
    # logger.info(f"{contents}")

    task_updated = dict()
    task_finished = []
    for task_id, content in contents.items():
        flag = False
        runtime_log_contents = dict()
        for log_path, log_content in content["raw_log_contents"].items():
            try:
                runtime_log_content = TaskService.parse_percent_log(log_path)
            except Exception as e:
                logger.warning(f"continue: warning monitor log,  \n {e}")
                continue
            runtime_log_contents[log_path] = runtime_log_content
            # to do, !=
            if runtime_log_content.timestamp != log_content["timestamp"]:
                flag = True

        if flag:
            print(runtime_log_contents)
            content_merged = TaskService.merge_percent_contents(runtime_log_contents)
            if content_merged.state in [TaskStateEnum.DONE, TaskStateEnum.ERROR]:
                task_finished.append(task_id)
            task_updated[task_id] = dict(
                raw_log_contents=runtime_log_contents,
                task_extra_info=content["task_extra_info"],
                percent_result=content_merged,
            )

    task_updated = StorageStructure.parse_obj(task_updated).dict()

    if len(task_updated):
        deal_updated_task(redis_client, task_updated, task_finished)


if __name__ == "__main__":
    sched = BlockingScheduler()
    sched.add_job(monitor_percent_log, "interval", seconds=5)
    sched.start()
