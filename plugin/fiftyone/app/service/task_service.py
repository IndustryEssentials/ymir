from loguru import logger
from celery.result import AsyncResult

from app.models.db import add_task, get_task, delete_task
from app.models.schemas import Task, TaskCreateResponse, TaskQueryResponse, TaskDeleteResponse
from app.worker import load_task_data
from utils.errors import FiftyOneResponseCode
from utils.constants import CeleryTaskStatus, FiftyoneTaskStatus
from conf.configs import conf


async def task_create(task: Task) -> dict:
    res = TaskCreateResponse()
    # check whether the task is already existed
    last_task = await get_task(task.tid)
    if last_task:
        res.code, res.error = (
            FiftyOneResponseCode.TASK_ALREADY_EXISTS,
            "task already existed",
        )
        return res.dict()
    celery_res = load_task_data.delay(task)
    celery_task_msg = {"tid": str(task.tid), "celery_id": celery_res.id}
    new_celery_task = await add_task(celery_task_msg)
    logger.info(f"new_celery_task: {new_celery_task}")

    res.data.tid = task.tid
    return res.dict()


async def task_query(tid: str) -> dict:
    res = TaskQueryResponse()
    # check whether the task is already existed
    task = await get_task(tid)
    if not task:
        res.code, res.error = (
            FiftyOneResponseCode.TASK_NOT_FOUND,
            f"can not find task by tid({tid})",
        )
        return res.dict()

    res.data.status = _celery_status_to_task_status(AsyncResult(task["celery_id"]).status)
    if res.data.status == FiftyoneTaskStatus.READY.value:
        res.data.url = conf.base_url + f"/fiftyone/datasets/{tid}"
    return res.dict()


def _celery_status_to_task_status(celery_status: str) -> str:
    if celery_status == CeleryTaskStatus.PENDING.value:
        task_status = FiftyoneTaskStatus.PENDING.value
    elif celery_status == CeleryTaskStatus.STARTED.value or celery_status == CeleryTaskStatus.RETRY.value:
        task_status = FiftyoneTaskStatus.PROCESSING.value
    elif celery_status == CeleryTaskStatus.SUCCESS.value:
        task_status = FiftyoneTaskStatus.READY.value
    elif celery_status == CeleryTaskStatus.FAILURE.value:
        task_status = FiftyoneTaskStatus.ERROR.value
    else:
        task_status = FiftyoneTaskStatus.OBSOLETE.value
    return task_status


async def task_delete(tid: str) -> dict:
    res = TaskDeleteResponse()
    task = await delete_task(tid)
    if not task:
        res.code, res.error = (
            FiftyOneResponseCode.TASK_NOT_FOUND.value,
            f"can not find task by tid({tid})",
        )
        return res.dict()

    return res.dict()
