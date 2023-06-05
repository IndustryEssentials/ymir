import asyncio
from datetime import datetime
import json
from typing import Any, Union, Optional
from functools import partial
import time

from fastapi import APIRouter, Depends, Path, Query, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from requests.exceptions import ConnectionError, HTTPError, Timeout
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import (
    FailedToUpdateTaskStatusTemporally,
    NoTaskPermission,
    ObsoleteTaskStatus,
    TaskNotFound,
    FailedToTerminateTask,
)
from app.constants.state import FinalStates, TaskState, TaskType
from app.config import settings
from app.utils.ymir_controller import ControllerClient
from app.libs.redis_stream import RedisStream
from app.libs.tasks import TaskResult, create_single_task
from app.libs.messages import message_filter
from common_utils.labels import UserLabels
from id_definition.task_id import gen_user_hash

router = APIRouter()


@router.post(
    "/batch",
    response_model=schemas.BatchTasksCreateResults,
)
def batch_create_tasks(
    *,
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
    batch_tasks_in: schemas.BatchTasksCreate,
) -> Any:
    f_create_task = partial(create_single_task, db, current_user.id, user_labels)

    results = []
    # run in iteration by design to avoid datasets version number conflicts
    for payload in batch_tasks_in.payloads:
        try:
            result = f_create_task(payload)
        except Exception:
            logger.exception("[batch create task] failed to create task by payload: %s", payload)
            result = None
        results.append(result)
    return {"result": results}


@router.get("/", response_model=schemas.TaskPaginationOut)
def list_tasks(
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    name: str = Query(None, description="search by task name"),
    type_: TaskType = Query(None, alias="type"),
    state: TaskState = Query(None),
    dataset_ids: str = Query(None, example="1,2,3"),
    model_stage_ids: str = Query(None, example="4,5,6"),
    pagination: schemas.CommonPaginationParams = Depends(),
) -> Any:
    """
    Get list of tasks,
    pagination is supported by means of offset and limit
    """
    tasks, total = crud.task.get_multi_tasks(
        db,
        user_id=current_user.id,
        name=name,
        type_=type_,
        state=state,
        dataset_ids=[int(i) for i in dataset_ids.split(",")] if dataset_ids else [],
        model_stage_ids=[int(i) for i in model_stage_ids.split(",")] if model_stage_ids else [],
        pagination=pagination,
    )
    return {"result": {"total": total, "items": tasks}}


@router.post("/", response_model=schemas.TaskOut)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Create task
    """
    logger.info("[create task] create task with payload: %s", jsonable_encoder(task_in))
    task_in_db = create_single_task(db, current_user.id, user_labels, task_in)
    logger.info("[create task] created task name: %s", task_in.name)
    return {"result": task_in_db}


@router.delete(
    "/{task_id}",
    response_model=schemas.TaskOut,
    dependencies=[Depends(deps.get_current_active_user)],
    responses={
        400: {"description": "No permission"},
        404: {"description": "Task Not Found"},
    },
)
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int = Path(..., example="12"),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete task
    (soft delete actually)
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise TaskNotFound()
    if task.user_id != current_user.id:
        raise NoTaskPermission()
    task = crud.task.soft_remove(db, id=task_id)
    return {"result": task}


@router.get(
    "/{task_id}",
    response_model=schemas.TaskOut,
    response_model_exclude_none=True,
    responses={404: {"description": "Task Not Found"}},
)
def get_task(
    db: Session = Depends(deps.get_db),
    task_id: int = Path(..., example="12"),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Get verbose information of specific task
    """
    task = crud.task.get_by_user_and_id(db, user_id=current_user.id, id=task_id)
    if not task:
        raise TaskNotFound()
    return {"result": task}


@router.post("/{task_id}/terminate", response_model=schemas.TaskOut)
def terminate_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int = Path(...),
    terminate_info: schemas.TaskTerminate,
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Terminate a task:

    if fetch_result, try to get task result and create related dataset or model
    otherwise, just set task state to terminated
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise TaskNotFound()
    try:
        controller_client.terminate_task(user_id=current_user.id, task_hash=task.hash, task_type=task.type)
    except ValueError:
        raise FailedToTerminateTask()
    task = crud.task.terminate(db, task=task)
    if not terminate_info.fetch_result:
        # task reachs final state right away
        # set result to error as well
        task = crud.task.update_state(db, task=task, new_state=TaskState.terminate)
        if task.result_model:
            crud.model.set_result_state_to_error(db, id=task.result_model.id)
        if task.result_dataset:
            crud.dataset.set_result_state_to_error(db, id=task.result_dataset.id)
    return {"result": task}


@router.post(
    "/status",
    response_model=schemas.TaskOut,
    dependencies=[Depends(deps.api_key_security)],
)
def update_task_status(
    *,
    db: Session = Depends(deps.get_db),
    request: Request,
    task_update: schemas.TaskUpdateStatus,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Update task status
    """
    # 1. Verification
    logger.info("[update task status] task %s, result: %s", task_update.hash, jsonable_encoder(task_update))
    task_in_db = crud.task.get_by_hash(db, hash_=task_update.hash)
    if not task_in_db:
        raise TaskNotFound()

    # 2. Remove obsolete msg
    if is_obsolete_message(task_in_db.last_message_timestamp, task_update.timestamp):
        logger.info("[update task status] ignore obsolete message")
        raise ObsoleteTaskStatus()

    task = schemas.TaskInternal.from_orm(task_in_db)
    if task.state in FinalStates:
        logger.warning("[update task status] Attempt to update finished task, skip")
        raise ObsoleteTaskStatus()

    # 3. Update task and task_result(could be dataset or model)
    task_result = TaskResult(db=db, task_in_db=task_in_db)
    try:
        task_in_db = task_result.update(task_result=task_update)
    except (ConnectionError, HTTPError, Timeout):
        logger.exception("[update task status] Failed to update task status. Try again later")
        raise FailedToUpdateTaskStatusTemporally()
    else:
        task_info = schemas.Task.from_orm(task_in_db)
        crud.task.update_last_message_datetime(db, id=task_info.id, dt=datetime.utcfromtimestamp(task_update.timestamp))
        namespace = f"/{gen_user_hash(task.user_id)}"
        task_update_msg = schemas.TaskResultUpdateMessage(
            task_id=task_info.hash,
            timestamp=time.time(),
            percent=task_info.percent,
            state=task_info.state,
            result_model=task_info.result_model,
            result_dataset=task_info.result_dataset,
            result_prediction=task_info.result_prediction,
            result_docker_image=task_info.result_docker_image,
        )
        payload = {task_info.hash: task_update_msg.dict()}
        asyncio.run(request.app.sio.emit(event="update_taskstate", data=payload, namespace=namespace))
        logger.info("notify task update (%s) to frontend (%s)", payload, namespace)
        if message_filter(task_info.state, task_info.type):
            msg = crud.message.create_message_from_task(db, task_info=task_info.dict())
            asyncio.run(
                request.app.sio.emit(
                    event="update_message", data=json.loads(schemas.Message.from_orm(msg).json()), namespace=namespace
                )
            )

    return {"result": task_in_db}


def is_obsolete_message(last_update_time: Optional[float], msg_time: Union[float, int]) -> bool:
    if last_update_time is None:
        # which means this is the first message for this task
        return False
    return last_update_time > msg_time


@router.post(
    "/events",
    response_model=schemas.TaskOut,
    dependencies=[Depends(deps.api_key_security)],
)
async def save_task_update_to_redis_stream(*, task_events: schemas.TaskMonitorEvents) -> Response:
    """
    Save task event to Redis Stream
    """
    redis_stream = RedisStream(settings.BACKEND_REDIS_URL)
    for event in task_events.events:
        await redis_stream.publish(event.json())
        logger.info("save task update to redis stream: %s", event.json())
    return Response(status_code=204)


@router.get(
    "/pai/{task_id}",
    response_model=schemas.task.PaiTaskOut,
    response_model_exclude_none=True,
    responses={404: {"description": "Task Not Found"}},
)
def get_openpai_task(
    db: Session = Depends(deps.get_db),
    task_id: int = Path(..., example=12),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Get verbose information of OpenPAI task
    """
    task = crud.task.get_by_user_and_id(db, user_id=current_user.id, id=task_id)
    if not task:
        raise TaskNotFound()
    # mixin openpai status
    return {"result": task}
