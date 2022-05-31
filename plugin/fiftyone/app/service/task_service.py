from loguru import logger

from app.models.db import add_task, get_task
from app.models.schemas import Task, BaseResponseBody
from app.worker import load_task_data


async def task_create(task: Task):
    res = BaseResponseBody()
    # check whether the task is already existed
    last_task = await get_task(task.tid)
    if last_task:
        res.code = 1002
        res.error = "task tid already exists"
        return res.dict
    celery_res = load_task_data(task)
    celery_task_msg = {"tid": str(task.tid), "celery_id": celery_res.id}
    new_celery_task = await add_task(celery_task_msg)
    logger.info(f"new_celery_task: {new_celery_task}")

    res.data["tid"] = task.tid
    return res.dict
