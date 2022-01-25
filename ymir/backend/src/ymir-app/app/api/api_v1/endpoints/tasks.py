import enum
import json
from datetime import datetime
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
from app.config import settings
from app.constants.state import FinalStates, TaskState, TaskType
from app.models import Dataset, Model
from app.models.task import Task
from app.schemas.task import MergeStrategy
from app.utils.class_ids import (
    get_keyword_id_to_name_mapping,
    get_keyword_name_to_id_mapping,
)
from app.utils.clickhouse import YmirClickHouse
from app.utils.email import send_task_result_email
from app.utils.err import catch_error_and_report
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
    response_model=schemas.TasksOut,
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
    if task_info["error_code"]:
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
        raise ObsoleteTaskStatus()

    task_info = schemas.TaskInternal.from_orm(task)
    if task_info.state in FinalStates:
        logger.warning("Attempt to update finished task, skip")
        raise ObsoleteTaskStatus()

    task_result_handler = TaskResultHandler(
        db=db,
        graph_db=graph_db,
        controller=controller_client,
        viz=viz_client,
        clickhouse=clickhouse,
    )
    try:
        updated_task = task_result_handler.save(task_info, task_result.dict())
    except (ConnectionError, HTTPError, Timeout):
        logger.error("Failed to update update task status")
        raise FailedToUpdateTaskStatus()
    except ModelNotReady:
        logger.warning("Model Not Ready")
        return {"result": task}

    if updated_task:
        updated_task = crud.task.update_last_message_datetime(
            db, task=updated_task, dt=datetime.utcfromtimestamp(task_result.timestamp)
        )
    result = updated_task or task
    return {"result": result}


def is_obsolete_message(
    last_update_time: Union[float, int], msg_time: Union[float, int]
) -> bool:
    return last_update_time > msg_time


class TaskResultHandler:
    def __init__(
        self,
        *,
        db: Session,
        graph_db: GraphClient,
        controller: ControllerClient,
        viz: VizClient,
        clickhouse: YmirClickHouse,
    ):
        self.db = db
        self.graph_db = graph_db
        self.controller = controller
        self.clickhouse = clickhouse
        self.viz = viz

    @staticmethod
    def should_fetch_task_result(previous_state: TaskState, state: TaskState) -> bool:
        if state is TaskState.done:
            return True
        # todo optimize
        #  task in premature state and reached finale, should fetch task result as well
        if previous_state is TaskState.premature and state in FinalStates:
            return True
        return False

    @staticmethod
    def is_valid_state(task_result: Dict) -> bool:
        if task_result and task_result["state"] != TaskState.unknown:
            logger.info("skip invalid task_result: %s", task_result)
            return True
        return False

    @staticmethod
    def is_failed_import_task(task_type: TaskType, task_state: TaskState) -> bool:
        return task_type is TaskType.import_data and task_state == TaskState.error

    def save(self, task: schemas.TaskInternal, task_result: Dict) -> Optional[Task]:
        """
        task: Pydantic Task Model
        task_result: Dict
            - state
            - percent
            - state_message  # to parse ignored keywords
        """
        if not self.is_valid_state(task_result):
            return None
        logger.debug(
            "task %s state: %s to %s", task.hash, task.state, task_result["state"]
        )

        if self.should_fetch_task_result(task.state, task_result["state"]):
            self.handle_finished_task(task)

        # special logic for failed import dataset task
        #  - add ignored keywords
        if self.is_failed_import_task(task.type, task_result["state"]):
            self.handle_failed_import_task(task, task_result.get("state_message"))

        updated_task = self.update_task_progress_and_state(
            task,
            task_result["state"],
            task_result["state_code"],
            task_result.get("percent", 0),
        )
        if not updated_task:
            logger.warning("task %s not updated", task.hash)
            return updated_task
        logger.debug(
            "task progress updated from %s to %s",
            task,
            schemas.Task.from_orm(updated_task),
        )

        if task_result["state"] in FinalStates:
            logger.debug("Sending notification for task: %s", task)
            self.send_notification(task, task_result["state"])

        return updated_task

    @catch_error_and_report
    def send_notification(self, task: schemas.Task, task_state: TaskState) -> None:
        creator = crud.user.get(self.db, id=task.user_id)
        if not (settings.EMAILS_ENABLED and creator and creator.email):
            return
        email = creator.email
        send_task_result_email(
            email,
            task.id,
            task.name,
            task.type.name,
            task_state.name,
        )

    def handle_finished_task(self, task: schemas.TaskInternal) -> None:
        logger.debug("fetching %s task result from %s", task.type, task.hash)
        if task.type is TaskType.training:
            model = self.add_new_model_if_not_exist(task)
            model_info = jsonable_encoder(model)
            logger.debug("task result(new model): %s", model_info)
            keywords = schemas.model.extract_keywords(task.parameters)
            try:
                self.clickhouse.save_model_result(
                    model.create_datetime,
                    model_info["user_id"],
                    model_info["id"],
                    model_info["name"],
                    model_info["hash"],
                    model_info["map"],
                    keywords,
                )
            except FailedToConnectClickHouse:
                logger.exception(
                    "[create task] failed to write model stats to clickhouse, continue anyway"
                )
            node = schemas.Model.from_orm(model)  # type: ignore
        elif task.type in [TaskType.mining, TaskType.label, TaskType.filter]:
            dataset = self.add_new_dataset_if_not_exist(task)
            logger.debug("task result(new dataset): %s", dataset)
            node = schemas.Dataset.from_orm(dataset)  # type: ignore
        elif task.type in [TaskType.import_data, TaskType.copy_data]:
            dataset = self.finish_dataset(task)  # type: ignore
            logger.debug("task result(finish dataset): %s", dataset)
            node = schemas.Dataset.from_orm(dataset)  # type: ignore
        else:
            logger.info("nothing to do for task: %s" % task)
            return

        parents = self.get_parent_nodes(task.parameters)  # type: ignore
        self.update_graph(parents=parents, node=node, task=task)
        logger.debug(
            "[graph] updated with parents: %s, node: %s and task: %s",
            parents,
            node,
            task,
        )

    def handle_failed_import_task(
        self, task: schemas.TaskInternal, state_message: Optional[str]
    ) -> None:
        # makeup data for failed dataset
        dataset_info = {
            "keywords": [],
            "ignored_keywords": self._parse_ignored_keywords(state_message),
            "items": 0,
            "total": 0,
        }
        logger.debug("[failed task] update dataset with %s", dataset_info)
        dataset = self.finish_dataset(task, dataset_info)
        logger.debug("[failed task] added ignored_keywords to dataset: %s", dataset)

    def _parse_ignored_keywords(self, error_message: Optional[str]) -> List[str]:
        if not error_message:
            return []
        try:
            ignored_keywords = list(json.loads(error_message).keys())
        except Exception:
            ignored_keywords = []
        return ignored_keywords

    def add_new_dataset_if_not_exist(self, task: schemas.TaskInternal) -> Dataset:
        dataset = crud.dataset.get_by_hash(self.db, hash_=task.hash)
        if dataset:
            # dataset already added before
            return dataset

        dataset_info = self.get_dataset_info(task.user_id, task.hash)
        dataset_in = schemas.DatasetCreate(
            name=get_default_record_name(task.hash, task.name),
            hash=task.hash,
            type=task.type,
            user_id=task.user_id,
            task_id=task.id,
            predicates=self._extract_keywords(dataset_info),
            asset_count=dataset_info["total"],
            keyword_count=len(dataset_info["keywords"]),
        )
        dataset = crud.dataset.create(self.db, obj_in=dataset_in)
        return dataset

    def finish_dataset(
        self, task: schemas.TaskInternal, dataset_info: Optional[Dict] = None
    ) -> Optional[Dataset]:
        dataset = crud.dataset.get_by_hash(self.db, hash_=task.hash)
        if not dataset:
            return dataset

        dataset_info = dataset_info or self.get_dataset_info(task.user_id, task.hash)
        dataset_in = schemas.DatasetUpdate(
            predicates=self._extract_keywords(dataset_info),
            asset_count=dataset_info["total"],
            keyword_count=len(dataset_info["keywords"]),
        )
        updated = crud.dataset.update(self.db, db_obj=dataset, obj_in=dataset_in)
        return updated

    def _extract_keywords(self, dataset_info: Dict) -> str:
        return json.dumps(
            {
                "keywords": dataset_info["keywords"],
                "ignored_keywords": dataset_info["ignored_keywords"],
            }
        )

    def add_new_model_if_not_exist(self, task: schemas.TaskInternal) -> Model:
        self.viz.config(user_id=task.user_id, branch_id=task.hash)
        model_info = self.viz.get_model()
        if not model_info:
            raise ModelNotReady()

        model = crud.model.get_by_hash(self.db, hash_=model_info["hash"])
        if model:
            # model already added before
            return model

        model_in = schemas.ModelCreate(
            name=get_default_record_name(task.hash, task.name),
            hash=model_info["hash"],
            map=model_info["map"],
            user_id=task.user_id,
            task_id=task.id,
        )
        model = crud.model.create(self.db, obj_in=model_in)
        return model

    def get_dataset_info(self, user_id: int, task_hash: str) -> Dict:
        labels = self.controller.get_labels_of_user(user_id)
        keyword_id_to_name = get_keyword_id_to_name_mapping(labels)
        self.viz.config(
            user_id=user_id, branch_id=task_hash, keyword_id_to_name=keyword_id_to_name
        )

        assets = self.viz.get_assets()
        result = {
            "keywords": list(assets.keywords.keys()),
            "ignored_keywords": list(assets.ignored_keywords.keys()),
            "items": assets.items,
            "total": assets.total,
        }
        return result

    def update_task_progress_and_state(
        self,
        task: schemas.TaskInternal,
        task_state: int,
        state_code: Optional[str],
        task_progress: float,
    ) -> Optional[Task]:
        task_obj = crud.task.get(self.db, id=task.id)
        if not task_obj:
            return task_obj
        task_progress = int(task_progress * 100)
        task_obj = crud.task.update_progress(
            self.db, task=task_obj, progress=task_progress
        )

        new_state = TaskState(task_state)
        if task_obj.state and TaskState(task_obj.state) is TaskState.premature:
            # ad hoc
            #  for task in premature state
            #  if state from Controller is done or error,
            #  we have to convert back to terminate for frontend
            #  otherwise just return so as to keep it's premature state
            new_state = (
                TaskState.terminate if new_state in FinalStates else TaskState.premature
            )
        task_obj = crud.task.update_state(
            self.db, task=task_obj, new_state=task.state, state_code=state_code
        )
        return task_obj

    def get_parent_nodes(self, parameters: Dict) -> List:
        """
        Parse task parameters to get input datasets and models for a task
        """
        dataset_ids = set()  # type: set
        for k, v in parameters.items():
            if k.endswith("datasets") and v:
                dataset_ids = dataset_ids.union(v)
        datasets = crud.dataset.get_multi_by_ids(self.db, ids=list(dataset_ids))
        datasets = [schemas.Dataset.from_orm(i) for i in datasets]  # type: ignore

        models = []
        model_id = parameters.get("model_id")
        if model_id:
            model = crud.model.get(self.db, id=model_id)
            if model:
                models = [schemas.Model.from_orm(model)]
        return datasets + models  # type: ignore

    @staticmethod
    def convert_to_graph_node(
        node: Union[schemas.Model, schemas.Dataset, schemas.TaskInternal]
    ) -> Dict:
        required_fields = ["hash", "id", "name", "type"]
        graph_node = {k: v for k, v in node.dict().items() if k in required_fields}
        graph_node["label"] = node.__repr_name__()
        if graph_node.get("type"):
            graph_node["type"] = graph_node["type"].value
        return graph_node

    def update_graph(
        self,
        *,
        parents: Optional[List] = None,
        node: Union[schemas.Dataset, schemas.Model],
        task: Optional[schemas.TaskInternal] = None,
    ) -> None:
        self.graph_db.user_id = task.user_id  # type: ignore
        graph_node = self.convert_to_graph_node(node)
        if parents and task:
            graph_task = self.convert_to_graph_node(task)
            for parent in parents:
                graph_parent = self.convert_to_graph_node(parent)
                self.graph_db.add_relationship(graph_parent, graph_node, graph_task)
        else:
            self.graph_db.add_node(graph_node)


def get_default_record_name(task_hash: str, task_name: str) -> str:
    return f"{task_name}_{task_hash[-6:]}"
