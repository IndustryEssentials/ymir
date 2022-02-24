import enum
from operator import attrgetter
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from requests.exceptions import ConnectionError, HTTPError, Timeout
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateTaskError,
    FailedToConnectClickHouse,
    FailedtoCreateTask,
    FailedToUpdateTaskStatus,
    ModelNotReady,
    NoTaskPermission,
    ObsoleteTaskStatus,
    TaskNotFound,
)
from app.constants.state import FinalStates, TaskState, TaskType
from app.models.task import Task
from app.schemas.task import MergeStrategy
from app.utils.class_ids import get_keyword_name_to_id_mapping
from app.utils.clickhouse import YmirClickHouse
from app.utils.graph import GraphClient
from app.utils.timeutil import convert_datetime_to_timestamp
from app.utils.ymir_controller import ControllerClient, ControllerRequest
from app.utils.ymir_viz import VizClient

router = APIRouter()


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
    response_model=schemas.TaskPaginationOut,
)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    current_workspace: models.Workspace = Depends(deps.get_current_workspace),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
    labels: List[str] = Depends(deps.get_personal_labels),
) -> Any:
    """
    Create task

    Note that if you selected multiple datasets, use `strategy` to choose primary one:
     - stop_upon_conflict = 1
     - prefer_newest = 2
     - prefer_oldest = 3
    """
    logger.debug(
        "[create task] create task with payload: %s", jsonable_encoder(task_in)
    )
    task = crud.task.get_by_user_and_name(
        db, user_id=current_user.id, name=task_in.name
    )
    if task:
        raise DuplicateTaskError()

    keyword_name_to_id = get_keyword_name_to_id_mapping(labels)

    # todo: using pydantic to do the normalization
    parameters = normalize_parameters(
        db, task_in.name, task_in.parameters, keyword_name_to_id
    )

    if parameters and task_in.config:
        parameters["docker_config"] = task_in.config

    try:
        task_id = ControllerRequest.gen_task_id(current_user.id)
        resp = controller_client.create_task(
            current_user.id,
            current_workspace.hash,
            task_id,
            task_in.type,
            parameters,
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        # todo parse error message
        raise FailedtoCreateTask()

    task = crud.task.create_task(
        db, obj_in=task_in, task_hash=task_id, user_id=current_user.id
    )

    try:
        # write clickhouse metric shouldn't block create task process
        metrics = parse_metrics(task_in.parameters.dict() if task_in.parameters else {})
        grouped_keywords = parameters.get("grouped_keywords", []) if parameters else []
        write_clickhouse_metrics(
            clickhouse,
            user_id=current_user.id,
            task=task,
            metrics=metrics,
            grouped_keywords=grouped_keywords,
        )
    except FailedToConnectClickHouse:
        logger.exception(
            "[create task] failed to write task(%s) stats to clickhouse, continue anyway",
            task.hash,
        )

    logger.info("[create task] created task name: %s" % task_in.name)
    return {"result": task}


def parse_metrics(parameters: Dict) -> Dict:
    if not parameters:
        return {"dataset_ids": [], "model_ids": [], "keywords": []}
    dataset_fields = [
        "include_datasets",
        "include_validation_datasets",
        "include_train_datasets",
        "include_test_datasets",
    ]
    dataset_ids = list(
        {
            dataset_id
            for field in dataset_fields
            for dataset_id in parameters.get(field) or []
        }
    )
    model_id = parameters.get("model_id")
    model_ids = [model_id] if model_id else []
    keywords = parameters.get("include_classes") or []
    return {"dataset_ids": dataset_ids, "model_ids": model_ids, "keywords": keywords}


def group_keywords_by_dataset(datasets: List[Dict], keywords: List[str]) -> List[Dict]:
    keywords_set = set(keywords)
    return [
        {
            "dataset_id": dataset["id"],
            "keywords": set(dataset["keywords"]) & keywords_set,
        }
        for dataset in datasets
    ]


def write_clickhouse_metrics(
    clickhouse: YmirClickHouse,
    *,
    user_id: int,
    task: Task,
    metrics: Dict,
    grouped_keywords: List,
) -> None:
    task_info = jsonable_encoder(task)
    clickhouse.save_task_parameter(
        dt=task.create_datetime,
        user_id=user_id,
        name=task_info["name"],
        hash_=task_info["hash"],
        type_=TaskType(task_info["type"]).name,
        **metrics,
    )
    for dataset_keywords in grouped_keywords:
        clickhouse.save_dataset_keyword(
            dt=task.create_datetime, user_id=user_id, **dataset_keywords
        )


def normalize_parameters(
    db: Session,
    name: str,
    parameters: Optional[schemas.TaskParameter],
    keyword_name_to_id: Dict,
) -> Optional[Dict]:
    """
    Normalize task parameters, including:
    - map class_name to class_id
    - map dataset_id to task_hash (which equates branch_id)
    """
    if not parameters:
        return None
    p = dict(parameters)
    normalized = {}  # type: Dict[str, Any]
    normalized["name"] = name
    unified_datasets = []
    for k, v in p.items():
        if v is None:
            continue
        if k.endswith("datasets"):
            datasets = crud.dataset.get_multi_by_ids(db, ids=v)
            unified_datasets.extend(
                [schemas.Dataset.from_orm(d).dict() for d in datasets]
            )
            order_datasets_by_strategy(datasets, parameters.strategy)
            normalized[k] = [dataset.hash for dataset in datasets]
        elif k.endswith("classes"):
            normalized[k] = [keyword_name_to_id[keyword.strip()] for keyword in v]
        elif k == "model_id":
            model = crud.model.get(db, id=v)
            if model and model.hash:
                normalized["model_hash"] = model.hash
        else:
            normalized[k] = v

    if unified_datasets and p.get("include_classes"):
        # if keywords is provided, we have to figure out
        # source dataset for each keyword
        normalized["grouped_keywords"] = group_keywords_by_dataset(
            unified_datasets, p["include_classes"]
        )
    return normalized


def order_datasets_by_strategy(
    objects: List[Any], strategy: Optional[MergeStrategy]
) -> None:
    """
    change the order of datasets *in place*
    """
    if not strategy:
        return
    if strategy is MergeStrategy.stop_upon_conflict:
        return
    return objects.sort(
        key=attrgetter("update_datetime"),
        reverse=strategy is MergeStrategy.prefer_newest,
    )


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
    task_info = jsonable_encoder(task)
    result = {}  # type: Dict[str, Any]
    model = crud.model.get_by_task_id(db, task_id=task_id)
    dataset = crud.dataset.get_by_task_id(db, task_id=task_id)
    if model:
        result["model_id"] = model.id
    if dataset:
        result["dataset_id"] = dataset.id
    if task_info["error_code"] and task_info["error_code"] != "0":
        result["error"] = {"code": task_info["error_code"]}

    task_info["result"] = result
    return {"result": task_info}


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
    task = crud.task.get_by_user_and_name(
        db, user_id=current_user.id, name=task_in.name
    )
    if task:
        raise DuplicateTaskError()

    task = crud.task.get(db, id=task_id)
    if not task:
        raise TaskNotFound()
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
    if not (task and task.hash and task.type):
        raise TaskNotFound()
    controller_client.terminate_task(
        user_id=current_user.id, task_hash=task.hash, task_type=task.type
    )

    new_state = (
        TaskState.premature if terminate_info.fetch_result else TaskState.terminate
    )
    task = crud.task.update_state(db, task=task, new_state=new_state)
    return {"result": task}


@router.post(
    "/status",
    response_model=schemas.TaskOut,
    dependencies=[Depends(deps.api_key_security)],
)
def update_task_status(
    *,
    db: Session = Depends(deps.get_db),
    task_result: schemas.TaskUpdateStatus,
    graph_db: GraphClient = Depends(deps.get_graph_client),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    viz_client: VizClient = Depends(deps.get_viz_client),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Update status of a task
    """
    logger.info(
        "[update status] task %s, result: %s",
        task_result.hash,
        jsonable_encoder(task_result),
    )
    task = crud.task.get_by_hash(db, hash_=task_result.hash)
    if not task:
        raise TaskNotFound()

    if is_obsolete_message(
        convert_datetime_to_timestamp(task.last_message_datetime), task_result.timestamp
    ):
        logger.debug("[update status] ignore obsolete message")
        raise ObsoleteTaskStatus()

    task_info = schemas.TaskInternal.from_orm(task)
    if task_info.state in FinalStates:
        logger.warning("Attempt to update finished task, skip")
        raise ObsoleteTaskStatus()

    try:
        updated_task = handle_task_result(task_info, task_result.dict())
    except (ConnectionError, HTTPError, Timeout):
        logger.error("Failed to update update task status")
        raise FailedToUpdateTaskStatus()
    except ModelNotReady:
        logger.warning("Model Not Ready")
        return {"result": task}

    result = updated_task or task
    return {"result": result}


def handle_task_result(task_info: Any, task_result: Dict) -> Dict:
    # todo
    return {}


def is_obsolete_message(
    last_update_time: Union[float, int], msg_time: Union[float, int]
) -> bool:
    return last_update_time > msg_time


def get_default_record_name(task_hash: str, task_name: str) -> str:
    return f"{task_name}_{task_hash[-6:]}"
