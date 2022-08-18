import json
import itertools
import asyncio
from typing import Any, Dict, List, Tuple, Optional

import aiohttp
from fastapi.logger import logger
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.errors.errors import (
    FailedToUpdateTaskStatus,
    FailedtoCreateTask,
    FailedToConnectClickHouse,
    ModelNotReady,
    ModelNotFound,
    ModelStageNotFound,
    TaskNotFound,
    DatasetNotFound,
    DatasetGroupNotFound,
    RequiredFieldMissing,
)
from app.constants.state import (
    FinalStates,
    TaskState,
    TaskType,
    ResultType,
    ResultState,
)
from app.config import settings
from app import schemas, crud, models
from app.utils.cache import CacheClient
from app.utils.ymir_controller import ControllerClient, gen_task_hash
from app.utils.clickhouse import YmirClickHouse
from app.utils.ymir_viz import VizClient
from common_utils.labels import UserLabels


class Retry(Exception):
    pass


async def should_retry(resp: aiohttp.ClientResponse) -> bool:
    if not resp.ok:
        # server returned 500, for example
        return True
    response = await resp.json()
    if int(response["code"]) == FailedToUpdateTaskStatus.code:
        # server explicitly asked for retry
        return True
    return False


async def post_task_update(session: aiohttp.ClientSession, payload: Dict) -> None:
    async with session.post(
        "http://localhost/api/v1/tasks/status", json=payload, headers={"api-key": settings.APP_API_KEY}
    ) as resp:
        if await should_retry(resp):
            raise Retry()


async def batch_update_task_status(events: List[Tuple[str, Dict]]) -> List[str]:
    ids, payloads = [], []
    for id_, msg in events:
        ids.append(id_)
        payloads.append(schemas.TaskUpdateStatus.from_monitor_event(msg["payload"]).dict())

    async with aiohttp.ClientSession() as session:
        tasks = [post_task_update(session, payload) for payload in payloads]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_id_selectors = [not isinstance(res, Exception) for res in results]
        return list(itertools.compress(ids, success_id_selectors))


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

    if parameters.model_stage_id:
        model_stage = crud.model_stage.get(db, id=parameters.model_stage_id)
        if not model_stage:
            raise ModelStageNotFound()
        normalized["model_hash"] = model_stage.model.hash  # type: ignore
        normalized["model_stage_name"] = model_stage.name

    if parameters.keywords:
        normalized["class_ids"] = user_labels.get_class_ids(names_or_aliases=parameters.keywords)

    if parameters.preprocess:
        normalized["preprocess"] = parameters.preprocess.json()
    return normalized


def write_clickhouse_metrics(
    task_info: schemas.TaskInternal,
    dataset_group_id: int,
    dataset_id: int,
    model_id: Optional[int],
    keywords: List[str],
) -> None:
    # for task stats
    clickhouse = YmirClickHouse()
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


def create_single_task(db: Session, user_id: int, user_labels: UserLabels, task_in: schemas.TaskCreate) -> models.Task:
    args = normalize_parameters(db, task_in.parameters, task_in.docker_image_config, user_labels)
    task_hash = gen_task_hash(user_id, task_in.project_id)
    try:
        controller_client = ControllerClient()
        resp = controller_client.create_task(
            user_id=user_id,
            project_id=task_in.project_id,
            task_id=task_hash,
            task_type=task_in.type,
            args=args,
            archived_task_parameters=task_in.parameters.json() if task_in.parameters else None,
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        raise FailedtoCreateTask()
    except KeyError:
        raise RequiredFieldMissing()

    task = crud.task.create_task(db, obj_in=task_in, task_hash=task_hash, user_id=user_id)
    task_info = schemas.TaskInternal.from_orm(task)

    task_result = TaskResult(db=db, task_in_db=task)
    task_result.create(task_in.parameters.dataset_id, task_in.result_description)

    try:
        write_clickhouse_metrics(
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
    logger.info("[create task] created task name: %s", task_info.name)
    return task


class TaskResult:
    def __init__(
        self,
        db: Session,
        task_in_db: models.Task,
    ):
        self.db = db
        self.task_in_db = task_in_db
        self.task = schemas.TaskInternal.from_orm(task_in_db)

        self.result_type = ResultType(self.task.result_type)
        self.user_id = self.task.user_id
        self.project_id = self.task.project_id
        self.task_hash = self.task.hash
        self.controller = ControllerClient()
        self.viz = VizClient()
        self.viz.initialize(
            user_id=self.user_id,
            project_id=self.project_id,
            branch_id=self.task_hash,
        )
        self.cache = CacheClient(user_id=self.user_id)

        self._result: Optional[Dict] = None
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
    def model_info(self) -> Optional[Dict]:
        try:
            result = self.viz.get_model_info()
        except (ModelNotReady, ModelNotFound):
            logger.exception("[update task] failed to get model_info: model not ready")
            return None
        except Exception:
            logger.exception("[update task] failed to get model_info: unknown error")
            return None
        else:
            return result

    @property
    def dataset_info(self) -> Optional[Dict]:
        try:
            dataset_info = self.viz.get_dataset_info(dataset_hash=self.task_hash, user_labels=self.user_labels)
        except Exception:
            logger.exception("[update task] failed to get dataset_info, check viz log")
            return None
        if dataset_info["new_types_added"]:
            logger.info("[update task] delete user keywords cache for new keywords from dataset")
            self.cache.delete_personal_keywords_cache()
        return dataset_info

    @property
    def result_info(self) -> Optional[Dict]:
        if self._result is None:
            self._result = self.model_info if self.result_type is ResultType.model else self.dataset_info
        return self._result

    def save_model_stats(self, result: Dict) -> None:
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
            result["hash"],
            result["map"],
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

    def create(self, dataset_id: int, description: Optional[str] = None) -> Dict[str, Dict]:
        dest_group_id, dest_group_name = self.get_dest_group_info(dataset_id)
        if self.result_type is ResultType.dataset:
            dataset = crud.dataset.create_as_task_result(
                self.db, self.task, dest_group_id, dest_group_name, description
            )
            logger.info("[create task] created new dataset(%s) as task result", dataset.name)
            return {"dataset": jsonable_encoder(dataset)}
        elif self.result_type is ResultType.model:
            model = crud.model.create_as_task_result(self.db, self.task, dest_group_id, dest_group_name, description)
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

    def update_task_result(self, task_result: schemas.TaskUpdateStatus, task_in_db: models.Task) -> None:
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

        if self.result_type is ResultType.model:
            # special path for model
            # as long as we can get model_info, set model as ready and
            # save related task parameters and config accordingly
            model_info = self.model_info
            logger.info(f"[viz_model] model_info: {model_info}")

            # todo refactor
            if model_info:
                crud.task.update_parameters_and_config(
                    self.db,
                    task=task_in_db,
                    parameters=model_info["task_parameters"],
                    config=json.dumps(model_info["executor_config"]),
                )
                current_model = crud.model.finish(
                    self.db, result_record.id, result_state=ResultState.ready, result=model_info
                )
                if current_model:
                    stages_in = []
                    for stage_name, body in model_info["model_stages"].items():
                        stage_obj = schemas.ModelStageCreate(
                            name=stage_name, map=body["mAP"], timestamp=body["timestamp"], model_id=current_model.id
                        )
                        stages_in.append(stage_obj)
                    crud.model_stage.batch_create(self.db, objs_in=stages_in)
                    crud.model.update_recommonded_stage_by_name(
                        self.db, model_id=current_model.id, stage_name=model_info["best_stage_name"]
                    )
                try:
                    self.save_model_stats(model_info)
                except FailedToConnectClickHouse:
                    logger.exception("Failed to write model stats to clickhouse, continue anyway")
                return

        if task_result.state is TaskState.done and self.result_info:
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
