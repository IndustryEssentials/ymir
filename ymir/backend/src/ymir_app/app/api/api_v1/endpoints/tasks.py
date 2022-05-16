import asyncio
import enum
from typing import Any, Union
from functools import partial
import time

from fastapi import APIRouter, Depends, Path, Query, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from requests.exceptions import ConnectionError, HTTPError, Timeout
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateTaskError,
    FailedToUpdateTaskStatus,
    ModelNotReady,
    NoTaskPermission,
    ObsoleteTaskStatus,
    TaskNotFound,
)
from app.constants.state import (
    FinalStates,
    TaskState,
    TaskType,
)
from app.config import settings
from app.utils.clickhouse import YmirClickHouse
from app.utils.graph import GraphClient
from app.utils.timeutil import convert_datetime_to_timestamp
from app.utils.ymir_controller import ControllerClient, gen_user_hash
from app.utils.ymir_viz import VizClient
from app.libs.redis_stream import RedisStream
from app.libs.tasks import TaskResult, create_single_task
from common_utils.labels import UserLabels

router = APIRouter()


@router.post(
    "/batch",
    response_model=schemas.BatchTasksCreateResults,
)
def batch_create_tasks(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
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


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"
    duration = "duration"


@router.get(
    "/",
    response_model=schemas.TaskPaginationOut,
)
def list_tasks(
    db: Session = Depends(deps.get_db),
    name: str = Query(None, description="search by task name"),
    type_: TaskType = Query(None, alias="type"),
    state: TaskState = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: SortField = Query(SortField.id),
    is_desc: bool = Query(True),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
    current_user: models.User = Depends(deps.get_current_active_user),
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
        offset=offset,
        limit=limit,
        order_by=order_by.name,
        is_desc=is_desc,
        start_time=start_time,
        end_time=end_time,
    )
    return {"result": {"total": total, "items": tasks}}


@router.post(
    "/",
    response_model=schemas.TaskOut,
)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Create task
    """
    # 1. validation
    logger.info("[create task] create task with payload: %s", jsonable_encoder(task_in))
    if crud.task.is_duplicated_name_in_project(db, project_id=task_in.project_id, name=task_in.name):
        raise DuplicateTaskError()

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
    current_user: models.User = Depends(deps.get_current_active_user),
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
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Get verbose information of specific task
    """
    task = crud.task.get_by_user_and_id(db, user_id=current_user.id, id=task_id)
    if not task:
        raise TaskNotFound()
    return {"result": task}


@router.patch(
    "/{task_id}",
    response_model=schemas.TaskOut,
    responses={404: {"description": "Task Not Found"}},
)
def update_task_name(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int = Path(..., example="12"),
    task_in: schemas.TaskUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update task name
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise TaskNotFound()
    if crud.task.is_duplicated_name_in_project(db, project_id=task.project_id, name=task_in.name):
        raise DuplicateTaskError()
    task = crud.task.update(db, db_obj=task, obj_in=task_in)
    return {"result": task}


@router.post(
    "/{task_id}/terminate",
    response_model=schemas.TaskOut,
)
def terminate_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int = Path(...),
    terminate_info: schemas.TaskTerminate,
    current_user: models.User = Depends(deps.get_current_active_user),
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
    controller_client.terminate_task(user_id=current_user.id, task_hash=task.hash, task_type=task.type)
    task = crud.task.terminate(db, task=task)
    if not terminate_info.fetch_result:
        # task reachs final state right away
        # set result to error as well
        task = crud.task.update_state(db, task=task, new_state=TaskState.terminate)
        if task.result_model:  # type: ignore
            crud.model.set_result_state_to_error(db, id=task.result_model.id)  # type: ignore
        if task.result_dataset:  # type: ignore
            crud.dataset.set_result_state_to_error(db, id=task.result_dataset.id)  # type: ignore
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
    graph_db: GraphClient = Depends(deps.get_graph_client),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    viz_client: VizClient = Depends(deps.get_viz_client),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Update status of a task
    """
    # 1. Verification
    logger.info(
        "[update status] task %s, result: %s",
        task_update.hash,
        jsonable_encoder(task_update),
    )
    task_in_db = crud.task.get_by_hash(db, hash_=task_update.hash)
    if not task_in_db:
        raise TaskNotFound()

    # 2. Remove obsolete msg
    if is_obsolete_message(
        convert_datetime_to_timestamp(task_in_db.last_message_datetime),
        task_update.timestamp,
    ):
        logger.info("[update status] ignore obsolete message")
        raise ObsoleteTaskStatus()

    task = schemas.TaskInternal.from_orm(task_in_db)
    if task.state in FinalStates:
        logger.warning("Attempt to update finished task, skip")
        raise ObsoleteTaskStatus()

    # 3. Update task and task_result(could be dataset or model)
    task_result = TaskResult(db=db, task_in_db=task_in_db)
    try:
        updated_task = task_result.update(task_result=task_update)
    except (ConnectionError, HTTPError, Timeout):
        logger.error("Failed to update update task status")
        raise FailedToUpdateTaskStatus()
    except ModelNotReady:
        logger.warning("Model Not Ready")
    else:
        namespace = f"/{gen_user_hash(task.user_id)}"
        task_update_msg = schemas.TaskResultUpdateMessage(
            task_id=updated_task.hash,
            timestamp=time.time(),
            percent=updated_task.percent,
            state=updated_task.state,
            result_model=updated_task.result_model,  # type: ignore
            result_dataset=updated_task.result_dataset,  # type: ignore
        )
        # todo compatible with current frontend data structure
        #  reformatting is needed
        payload = {updated_task.hash: task_update_msg.dict()}
        asyncio.run(request.app.sio.emit(event="update_taskstate", data=payload, namespace=namespace))

    return {"result": task_in_db}


def is_obsolete_message(last_update_time: Union[float, int], msg_time: Union[float, int]) -> bool:
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
