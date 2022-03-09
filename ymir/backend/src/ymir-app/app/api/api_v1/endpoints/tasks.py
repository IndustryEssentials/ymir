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
    DatasetNotFound,
    ModelNotFound,
)
from app.constants.state import FinalStates, TaskState, TaskType, ResultType
from app.schemas.task import MergeStrategy
from app.utils.class_ids import get_keyword_name_to_id_mapping
from app.utils.clickhouse import YmirClickHouse
from app.utils.graph import GraphClient
from app.utils.timeutil import convert_datetime_to_timestamp
from app.utils.ymir_controller import ControllerClient, gen_task_hash
from app.utils.ymir_viz import VizClient

router = APIRouter()


class NoDestGroup(Exception):
    pass


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
    # 1. validation
    task_info = jsonable_encoder(task_in)
    logger.debug("[create task] create task with payload: %s", task_info)
    if crud.task.is_duplicated_name(db, user_id=current_user.id, name=task_in.name):
        raise DuplicateTaskError()

    # 2. prepare keywords and task parameters
    keyword_name_to_id = get_keyword_name_to_id_mapping(labels)
    parameters = normalize_parameters(
        db, task_in.name, task_in.parameters, keyword_name_to_id
    )
    if parameters and task_in.config:
        parameters["docker_config"] = task_in.config

    # 3. call controller
    task_hash = gen_task_hash(current_user.id, task_in.project_id)
    try:
        resp = controller_client.create_task(
            current_user.id,
            task_in.project_id,
            task_hash,
            task_in.type,
            parameters,
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        # todo parse error message
        raise FailedtoCreateTask()

    # 4. create task record
    task = crud.task.create_task(
        db, obj_in=task_in, task_hash=task_hash, user_id=current_user.id
    )

    # 5. create task result record (dataset or model)
    task_result = TaskResult(db=db, task_in_db=task)
    task_result.create(task_in.dest_group_id, task_in.parameters.dataset_id)  # type: ignore

    # 6. send metric to clickhouse
    try:
        metrics = parse_metrics(task_in.parameters.dict() if task_in.parameters else {})
        grouped_keywords = parameters.get("grouped_keywords", []) if parameters else []
        write_clickhouse_metrics(clickhouse, task_info, metrics, grouped_keywords)
    except FailedToConnectClickHouse:
        # write clickhouse metric shouldn't block create task process
        logger.exception(
            "[create task] failed to write task(%s) stats to clickhouse, continue anyway",
            task.hash,
        )
    logger.info("[create task] created task name: %s" % task_in.name)
    return {"result": task}


class TaskResult:
    def __init__(self, db: Session, task_in_db: models.Task):
        self.db = db
        self.task_in_db = task_in_db
        self.task = schemas.TaskInternal.from_orm(task_in_db)

    def get_dest_group_id(self, dataset_id: int) -> int:
        if self.task.result_type is ResultType.dataset:
            dataset = crud.dataset.get(self.db, id=dataset_id)
            if not dataset:
                raise NoDestGroup("Failed to predict dest dataset group id")
            return dataset.dataset_group_id
        else:
            model_group = crud.model_group.get_from_training_dataset(
                self.db, training_dataset_id=dataset_id
            )
            if not model_group:
                raise NoDestGroup("Failed to predict dest model group id")
            return model_group.id

    def create(self, dest_group_id: Optional[int], dataset_id: int) -> None:
        dest_group_id = dest_group_id or self.get_dest_group_id(dataset_id)
        if self.task.result_type is ResultType.dataset:
            logger.info("[create task] creating new dataset as task result")
            crud.dataset.create_as_task_result(self.db, self.task, dest_group_id)
        elif self.task.result_type is ResultType.model:
            logger.info("[create task] creating new model as task result")
            crud.model.create_as_task_result(self.db, self.task, dest_group_id)
        else:
            logger.info("[create task] no task result record needed")

    def update(self, task_result: schemas.TaskUpdateStatus) -> models.Task:
        if self.task.result_type is ResultType.dataset:
            self.update_dataset_result(task_result)
        elif self.task.result_type is ResultType.model:
            self.update_model_result(task_result)
        else:
            logger.info("[update task] no task result to update")

        task_in_db = crud.task.get(self.db, id=self.task.id)
        if not task_in_db:
            raise TaskNotFound()
        return crud.task.update_state_and_percent(
            self.db,
            task=task_in_db,
            new_state=task_result.state,
            state_code=task_result.state_code,
            percent=task_result.percent,
        )

    def update_dataset_result(self, task_result: schemas.TaskUpdateStatus) -> None:
        dataset = crud.dataset.get_by_task_id(self.db, task_id=self.task.id)
        if not dataset:
            raise DatasetNotFound()
        crud.dataset.update_state(
            # already fix the type in PR 352, remove it when merged 352
            self.db,
            dataset_id=dataset.id,
            new_state=task_result.state,  # type: ignore
        )

    def update_model_result(self, task_result: schemas.TaskUpdateStatus) -> None:
        model = crud.model.get_by_task_id(self.db, task_id=self.task.id)
        if not model:
            raise ModelNotFound()
        crud.model.update_state(self.db, model_id=model.id, new_state=task_result.state)


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
    task_info: Dict,
    metrics: Dict,
    grouped_keywords: List,
) -> None:
    clickhouse.save_task_parameter(
        dt=task_info["create_datetime"],
        user_id=task_info["user_id"],
        name=task_info["name"],
        hash_=task_info["hash"],
        type_=TaskType(task_info["type"]).name,
        **metrics,
    )
    for dataset_keywords in grouped_keywords:
        clickhouse.save_dataset_keyword(
            dt=task_info["create_datetime"],
            user_id=task_info["user_id"],
            **dataset_keywords,
        )


def normalize_parameters(
    db: Session,
    name: str,
    parameters: Optional[schemas.TaskParameter],
    keyword_name_to_id: Dict,
) -> Optional[Dict]:
    if not parameters:
        return None
    normalized = {}  # type: Dict[str, Any]
    normalized["name"] = name

    dataset = crud.dataset.get(db, id=parameters.dataset_id)
    if not dataset:
        raise DatasetNotFound()
    normalized["dataset_hash"] = dataset.hash

    if parameters.model_id:
        model = crud.model.get(db, id=parameters.model_id)
        if model:
            normalized["model_hash"] = model.hash

    if parameters.keywords:
        normalized["class_ids"] = [
            keyword_name_to_id[keyword.strip()] for keyword in parameters.keywords
        ]
        # if keywords is provided, we have to figure out
        # source dataset for each keyword
        normalized["grouped_keywords"] = group_keywords_by_dataset(
            [jsonable_encoder(dataset)],
            parameters.keywords,
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
        logger.debug("[update status] ignore obsolete message")
        raise ObsoleteTaskStatus()

    task = schemas.TaskInternal.from_orm(task_in_db)
    if task.state in FinalStates:
        logger.warning("Attempt to update finished task, skip")
        raise ObsoleteTaskStatus()

    # 3. Update task and task_result(could be dataset or model)
    task_result = TaskResult(db=db, task_in_db=task_in_db)
    try:
        task_in_db = task_result.update(task_result=task_update)
    except (ConnectionError, HTTPError, Timeout):
        logger.error("Failed to update update task status")
        raise FailedToUpdateTaskStatus()
    except ModelNotReady:
        logger.warning("Model Not Ready")

    return {"result": task_in_db}


def is_obsolete_message(
    last_update_time: Union[float, int], msg_time: Union[float, int]
) -> bool:
    return last_update_time > msg_time


def get_default_record_name(task_hash: str, task_name: str) -> str:
    return f"{task_name}_{task_hash[-6:]}"
