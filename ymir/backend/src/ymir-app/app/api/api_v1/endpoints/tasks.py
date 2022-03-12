import enum
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
)
from app.constants.state import (
    FinalStates,
    TaskState,
    TaskType,
    ResultType,
    ResultState,
)
from app.utils.clickhouse import YmirClickHouse
from app.utils.graph import GraphClient
from app.utils.timeutil import convert_datetime_to_timestamp
from app.utils.ymir_controller import ControllerClient, gen_task_hash
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
    response_model=schemas.TaskOut,
)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    viz_client: VizClient = Depends(deps.get_viz_client),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
    personal_labels: Dict = Depends(deps.get_personal_labels),
) -> Any:
    """
    Create task
    """
    # 1. validation
    task_info = jsonable_encoder(task_in)
    logger.debug("[create task] create task with payload: %s", task_info)
    if crud.task.is_duplicated_name(db, user_id=current_user.id, name=task_in.name):
        raise DuplicateTaskError()

    # 2. prepare keywords and task parameters
    parameters = normalize_parameters(db, task_in.parameters, task_in.config, personal_labels)

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
    task = crud.task.create_task(db, obj_in=task_in, task_hash=task_hash, user_id=current_user.id)

    # 5. create task result record (dataset or model)
    task_result = TaskResult(db=db, controller=controller_client, viz=viz_client, task_in_db=task)
    task_result.create(task_in.parameters.dataset_id)

    # 6. send metric to clickhouse
    try:
        write_clickhouse_metrics(
            clickhouse,
            jsonable_encoder(task),
            task_in.parameters.dataset_id,
            task_in.parameters.model_id,
            task_in.parameters.keywords or [],
        )
    except FailedToConnectClickHouse:
        # write clickhouse metric shouldn't block create task process
        logger.exception(
            "[create task] failed to write task(%s) stats to clickhouse, continue anyway",
            task.hash,
        )
    logger.info("[create task] created task name: %s" % task_in.name)
    return {"result": task}


class TaskResult:
    def __init__(
        self,
        db: Session,
        controller: ControllerClient,
        viz: VizClient,
        task_in_db: models.Task,
    ):
        self.db = db
        self.task_in_db = task_in_db
        self.task = schemas.TaskInternal.from_orm(task_in_db)

        self.result_type = self.task.result_type
        self.user_id = self.task.user_id
        self.project_id = self.task.project_id
        self.task_hash = self.task.hash
        self.controller = controller

        viz.initialize(
            user_id=self.user_id,
            project_id=self.project_id,
            branch_id=self.task_hash,
        )
        self.viz = viz

    @property
    def personal_labels(self) -> Dict:
        """
        Lazy evaluate labels from controller
        """
        return self.controller.get_labels_of_user(self.user_id)

    @property
    def model_info(self) -> Dict:
        return self.viz.get_model()

    @property
    def dataset_info(self) -> Dict:
        assets = self.viz.get_assets(personal_labels=self.personal_labels)
        result = {
            "keywords": list(assets.keywords.keys()),
            "ignored_keywords": list(assets.ignored_keywords.keys()),
            "asset_count": assets.total,
        }
        return result

    @property
    def result_info(self) -> Dict:
        return self.model_info if self.result_type is ResultType.model else self.dataset_info

    def get_dest_group_id(self, dataset_id: int) -> int:
        if self.result_type is ResultType.dataset:
            dataset = crud.dataset.get(self.db, id=dataset_id)
            if not dataset:
                logger.error(
                    "Failed to predict dest dataset_group_id from non-existing dataset(%s)",
                    dataset_id,
                )
                raise DatasetNotFound()
            return dataset.dataset_group_id
        else:
            model_group = crud.model_group.get_from_training_dataset(self.db, training_dataset_id=dataset_id)
            if not model_group:
                model_group = crud.model_group.create_model_group(
                    self.db,
                    user_id=self.user_id,
                    project_id=self.project_id,
                    training_dataset_id=dataset_id,
                )
                logger.info(
                    "[create task] created model_group(%s) for dataset(%s)",
                    model_group.id,
                    dataset_id,
                )
            return model_group.id

    def create(self, dataset_id: int) -> None:
        dest_group_id = self.get_dest_group_id(dataset_id)
        if self.result_type is ResultType.dataset:
            logger.info("[create task] creating new dataset as task result")
            crud.dataset.create_as_task_result(self.db, self.task, dest_group_id)
        elif self.result_type is ResultType.model:
            logger.info("[create task] creating new model as task result")
            crud.model.create_as_task_result(self.db, self.task, dest_group_id)
        else:
            logger.info("[create task] no task result record needed")

    def update(
        self,
        viz: VizClient,
        controller: ControllerClient,
        task_result: schemas.TaskUpdateStatus,
    ) -> models.Task:
        task_in_db = crud.task.get(self.db, id=self.task.id)
        if not task_in_db:
            logger.error(
                "[update task] could not find target task (%s) to update, ignore",
                self.task.id,
            )
            raise TaskNotFound()

        if task_result.state in FinalStates:
            logger.info(
                "[update task] task reached final state(%s), handling result: %s",
                task_result.state,
                task_result,
            )
            self.update_task_result(task_result)

        logger.info(
            "[update task] updating task state %s and percent %s",
            task_result.state,
            task_result.percent,
        )
        return crud.task.update_state_and_percent(
            self.db,
            task=task_in_db,
            new_state=task_result.state,
            state_code=task_result.state_code,
            percent=task_result.percent,
        )

    def update_task_result(self, task_result: schemas.TaskUpdateStatus) -> None:
        if self.result_type is ResultType.dataset:
            crud_func = crud.dataset
        elif self.result_type is ResultType.model:
            crud_func = crud.model  # type: ignore
        else:
            logger.info("[update task] no task result to update")
            return

        result_record = crud_func.get_by_task_id(self.db, task_id=self.task.id)
        if not result_record:
            logger.error("[update task] task result record not found, skip")
            return

        if task_result.state is TaskState.done:
            crud_func.finish(
                self.db,
                result_record.id,
                result_state=ResultState.ready,
                result=self.result_info,
            )
        else:
            crud_func.finish(
                self.db,
                result_record.id,
                result_state=ResultState.error,
            )


def write_clickhouse_metrics(
    clickhouse: YmirClickHouse,
    task_info: Dict,
    dataset_id: int,
    model_id: Optional[int],
    keywords: List[str],
) -> None:
    clickhouse.save_task_parameter(
        dt=task_info["create_datetime"],
        user_id=task_info["user_id"],
        name=task_info["name"],
        hash_=task_info["hash"],
        type_=TaskType(task_info["type"]).name,
        dataset_ids=[dataset_id],
        model_ids=[model_id] if model_id else [],
        keywords=keywords,
    )
    clickhouse.save_dataset_keyword(
        dt=task_info["create_datetime"],
        user_id=task_info["user_id"],
        dataset_id=dataset_id,
        keywords=keywords,
    )


def normalize_parameters(
    db: Session,
    parameters: schemas.TaskParameter,
    config: Optional[Dict],
    personal_labels: Dict,
) -> Dict:
    normalized = parameters.dict()  # type: Dict[str, Any]

    # training, mining and inference task has docker_config
    normalized["docker_config"] = config

    dataset = crud.dataset.get(db, id=parameters.dataset_id)
    if not dataset:
        logger.error("[create task] main dataset(%s) not exists", parameters.dataset_id)
        raise DatasetNotFound()
    normalized["dataset_hash"] = dataset.hash
    # label task uses dataset name as task name for LabelStudio
    normalized["dataset_name"] = dataset.name

    if parameters.validation_dataset_id:
        validation_dataset = crud.dataset.get(db, id=parameters.validation_dataset_id)
        if not validation_dataset:
            logger.error("[create task] validation dataset(%s) not exists", parameters.validation_dataset_id)
            raise DatasetNotFound()
        normalized["validation_dataset_hash"] = validation_dataset.hash

    if parameters.model_id:
        model = crud.model.get(db, id=parameters.model_id)
        if model:
            normalized["model_hash"] = model.hash

    if parameters.keywords:
        normalized["class_ids"] = [personal_labels["name_to_id"][keyword]["id"] for keyword in parameters.keywords]
    return normalized


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
    task = crud.task.get_by_user_and_name(db, user_id=current_user.id, name=task_in.name)
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
    if not task:
        raise TaskNotFound()
    controller_client.terminate_task(user_id=current_user.id, task_hash=task.hash, task_type=task.type)
    task = crud.task.terminate(db, task=task)
    if not terminate_info.fetch_result:
        # task that is terminated without result is in final terminate state
        task = crud.task.update_state(db, task=task, new_state=TaskState.terminate)
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
    task_result = TaskResult(db=db, controller=controller_client, viz=viz_client, task_in_db=task_in_db)
    try:
        task_in_db = task_result.update(viz=viz_client, controller=controller_client, task_result=task_update)
    except (ConnectionError, HTTPError, Timeout):
        logger.error("Failed to update update task status")
        raise FailedToUpdateTaskStatus()
    except ModelNotReady:
        logger.warning("Model Not Ready")

    return {"result": task_in_db}


def is_obsolete_message(last_update_time: Union[float, int], msg_time: Union[float, int]) -> bool:
    return last_update_time > msg_time


def get_default_record_name(task_hash: str, task_name: str) -> str:
    return f"{task_name}_{task_hash[-6:]}"
