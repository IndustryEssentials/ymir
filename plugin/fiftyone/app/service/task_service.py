from loguru import logger

from app.models.db import add_task, get_task
from app.models.schemas import Task, TaskCreateResponse
from app.worker import load_task_data
from conf.configs import conf
from utils.errors import FiftyOneResponseCode


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
    if conf.debug is True:
        load_task_data(task)
        celery_task_msg = {"tid": str(task.tid), "celery_id": "32423423423"}
    else:
        celery_res = load_task_data.delay(task)
        celery_task_msg = {"tid": str(task.tid), "celery_id": celery_res.id}
    new_celery_task = await add_task(celery_task_msg)
    logger.info(f"new_celery_task: {new_celery_task}")

    res.data.tid = task.tid
    return res.dict()
