import asyncio
from dataclasses import asdict
import enum
import json
from typing import Any, Dict, List, Optional, Union, Tuple
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
    FailedToConnectClickHouse,
    FailedtoCreateTask,
    FailedToUpdateTaskStatus,
    ModelNotFound,
    ModelNotReady,
    NoTaskPermission,
    ObsoleteTaskStatus,
    TaskNotFound,
    DatasetNotFound,
    DatasetGroupNotFound,
)
from app.constants.state import (
    FinalStates,
    TaskState,
    TaskType,
    ResultType,
    ResultState,
)
from app.config import settings
from app.models.task import Task
from app.utils.clickhouse import YmirClickHouse
from app.utils.graph import GraphClient
from app.utils.timeutil import convert_datetime_to_timestamp
from app.utils.ymir_controller import ControllerClient, gen_task_hash, gen_user_hash
from app.utils.ymir_viz import VizClient, ModelMetaData, DatasetMetaData
from app.libs.redis_stream import RedisStream
from common_utils.labels import UserLabels

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
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Create task
    """
    # 1. validation
    logger.debug("[create task] create task with payload: %s", jsonable_encoder(task_in))
    if crud.task.is_duplicated_name_in_project(db, project_id=task_in.project_id, name=task_in.name):
        raise DuplicateTaskError()

    # 2. prepare keywords and task parameters
    args = normalize_parameters(db, task_in.parameters, task_in.docker_image_config, user_labels)

    # 3. call controller
    task_hash = gen_task_hash(current_user.id, task_in.project_id)
    try:
        resp = controller_client.create_task(
            user_id=current_user.id,
            project_id=task_in.project_id,
            task_id=task_hash,
            task_type=task_in.type,
            args=args,
            task_parameters=task_in.parameters.json() if task_in.parameters else None,
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        # todo parse error message
        raise FailedtoCreateTask()

    # 4. create task record
    task = crud.task.create_task(db, obj_in=task_in, task_hash=task_hash, user_id=current_user.id)
    task_info = schemas.TaskInternal.from_orm(task)

    # 5. create task result record (dataset or model)
    task_result = TaskResult(db=db, controller=controller_client, viz=viz_client, task_in_db=task)
    task_result.create(task_in.parameters.dataset_id)

    # 6. send metric to clickhouse
    try:
        write_clickhouse_metrics(
            clickhouse,
            task_info,
            args["dataset_group_id"],
            args["dataset_id"],
            task_in.parameters.model_id,
            task_in.parameters.keywords or [],
        )
    except FailedToConnectClickHouse:
        # clickhouse metric shouldn't block create task process
        logger.exception(
            "[create task] failed to write task(%s) stats to clickhouse, continue anyway",
            task.hash,
        )
    logger.info("[create task] created task name: %s", task_in.name)

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

        self.result_type = ResultType(self.task.result_type)
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

        self._result: Optional[Union[DatasetMetaData, ModelMetaData]] = None
        self._user_labels: Optional[Dict] = None

    @property
    def user_labels(self) -> Dict:
        """
        Lazy evaluate labels from controller
        """
        if self._user_labels is None:
            self._user_labels = self.controller.get_labels_of_user(self.user_id)
        return self._user_labels

    @property
    def model_info(self) -> ModelMetaData:
        result = self.viz.get_model()
        try:
            self.save_model_stats(result)
        except FailedToConnectClickHouse:
            logger.exception("Failed to write model stats to clickhouse, continue anyway")
        return result

    @property
    def dataset_info(self) -> DatasetMetaData:
        return self.viz.get_dataset(user_labels=self.user_labels)

    @property
    def result_info(self) -> Union[DatasetMetaData, ModelMetaData]:
        if self._result is None:
            self._result = self.model_info if self.result_type is ResultType.model else self.dataset_info
        return self._result

    def save_model_stats(self, result: ModelMetaData) -> None:
        model_in_db = crud.model.get_by_task_id(self.db, task_id=self.task.id)
        if not model_in_db:
            logger.warning("[update task] found no model to save model stats(%s)", result)
            return
        project_in_db = crud.project.get(self.db, id=self.project_id)
        keywords = schemas.Project.from_orm(project_in_db).training_keywords
        clickhouse = YmirClickHouse()
        clickhouse.save_model_result(
            model_in_db.create_datetime,
            self.user_id,
            model_in_db.project_id,
            model_in_db.model_group_id,
            model_in_db.id,
            model_in_db.name,
            result.hash,
            result.map,
            keywords,
        )

    def get_dest_group_info(self, dataset_id: int) -> Tuple[int, str]:
        if self.result_type is ResultType.dataset:
            dataset = crud.dataset.get(self.db, id=dataset_id)
            if not dataset:
                logger.error(
                    "Failed to predict dest dataset_group_id from non-existing dataset(%s)",
                    dataset_id,
                )
                raise DatasetNotFound()
            dataset_group = crud.dataset_group.get(self.db, id=dataset.dataset_group_id)
            if not dataset_group:
                raise DatasetGroupNotFound()
            return dataset_group.id, dataset_group.name
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
            return model_group.id, model_group.name

    def create(self, dataset_id: int) -> Dict[str, Dict]:
        dest_group_id, dest_group_name = self.get_dest_group_info(dataset_id)
        if self.result_type is ResultType.dataset:
            dataset = crud.dataset.create_as_task_result(self.db, self.task, dest_group_id, dest_group_name)
            logger.info("[create task] created new dataset(%s) as task result", dataset.name)
            return {"dataset": jsonable_encoder(dataset)}
        elif self.result_type is ResultType.model:
            model = crud.model.create_as_task_result(self.db, self.task, dest_group_id, dest_group_name)
            logger.info("[create task] created new model(%s) as task result", model.name)
            return {"model": jsonable_encoder(model)}
        else:
            logger.info("[create task] no task result record needed")
            return {}

    def update(
        self,
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
            self.update_task_result(task_result, task_in_db)

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

    def update_task_result(self, task_result: schemas.TaskUpdateStatus, task_in_db: Task) -> None:
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
            if isinstance(self.result_info, ModelMetaData):
                crud.task.update_parameters_and_config(
                    self.db,
                    task=task_in_db,
                    parameters=self.result_info.task_parameters,
                    config=json.dumps(self.result_info.executor_config),
                )
            crud_func.finish(
                self.db,
                result_record.id,
                result_state=ResultState.ready,
                result=asdict(self.result_info),
            )
        else:
            if self.result_type is ResultType.model:
                try:
                    crud.model.finish(
                        self.db, result_record.id, result_state=ResultState.ready, result=asdict(self.model_info)
                    )
                except (ModelNotReady, ModelNotFound):
                    logger.exception("[update task] failed to get model from failed task")
                    crud_func.finish(
                        self.db,
                        result_record.id,
                        result_state=ResultState.error,
                    )
            else:
                crud_func.finish(
                    self.db,
                    result_record.id,
                    result_state=ResultState.error,
                )


def write_clickhouse_metrics(
    clickhouse: YmirClickHouse,
    task_info: schemas.TaskInternal,
    dataset_group_id: int,
    dataset_id: int,
    model_id: Optional[int],
    keywords: List[str],
) -> None:
    # for task stats
    clickhouse.save_task_parameter(
        dt=task_info.create_datetime,
        user_id=task_info.user_id,
        project_id=task_info.project_id,
        name=task_info.name,
        hash_=task_info.hash,
        type_=TaskType(task_info.type).name,
        dataset_ids=[dataset_id],
        model_ids=[model_id] if model_id else [],
        keywords=keywords,
    )
    # for keywords recommendation
    clickhouse.save_dataset_keyword(
        dt=task_info.create_datetime,
        user_id=task_info.user_id,
        project_id=task_info.project_id,
        group_id=dataset_group_id,
        dataset_id=dataset_id,
        keywords=keywords,
    )


def normalize_parameters(
    db: Session,
    parameters: schemas.TaskParameter,
    docker_image_config: Optional[Dict],
    user_labels: UserLabels,
) -> Dict:
    normalized = parameters.dict()  # type: Dict[str, Any]

    # training, mining and inference task has docker_config
    normalized["docker_config"] = docker_image_config

    dataset = crud.dataset.get(db, id=parameters.dataset_id)
    if not dataset:
        logger.error("[create task] main dataset(%s) not exists", parameters.dataset_id)
        raise DatasetNotFound()
    normalized["dataset_hash"] = dataset.hash
    normalized["dataset_group_id"] = dataset.dataset_group_id
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
        normalized["class_ids"] = user_labels.get_class_ids(names_or_aliases=parameters.keywords)
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
        logger.debug("[update status] ignore obsolete message")
        raise ObsoleteTaskStatus()

    task = schemas.TaskInternal.from_orm(task_in_db)
    if task.state in FinalStates:
        logger.warning("Attempt to update finished task, skip")
        raise ObsoleteTaskStatus()

    # 3. Update task and task_result(could be dataset or model)
    task_result = TaskResult(db=db, controller=controller_client, viz=viz_client, task_in_db=task_in_db)
    try:
        task_in_db = task_result.update(task_result=task_update)
    except (ConnectionError, HTTPError, Timeout):
        logger.error("Failed to update update task status")
        raise FailedToUpdateTaskStatus()
    except ModelNotReady:
        logger.warning("Model Not Ready")

    namespace = f"/{gen_user_hash(task.user_id)}"
    task_update_msg = schemas.TaskResultUpdateMessage(
        task_id=task_in_db.hash,
        timestamp=time.time(),
        percent=task_in_db.percent,
        state=task_in_db.state,
        result_model=task_in_db.result_model,  # type: ignore
        result_dataset=task_in_db.result_dataset,  # type: ignore
    )
    # todo compatible with current frontend data structure
    #  reformatting is needed
    payload = {task_in_db.hash: task_update_msg.dict()}
    asyncio.run(request.app.sio.emit(event="update_taskstate", data=payload, namespace=namespace))

    return {"result": task_in_db}


def is_obsolete_message(last_update_time: Union[float, int], msg_time: Union[float, int]) -> bool:
    return last_update_time > msg_time


def get_default_record_name(task_hash: str, task_name: str) -> str:
    return f"{task_name}_{task_hash[-6:]}"


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
