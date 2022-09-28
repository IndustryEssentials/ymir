from functools import cached_property
import json
import itertools
import asyncio
from typing import Any, Dict, List, Tuple, Optional

import aiohttp
from fastapi.logger import logger
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.errors.errors import (
    DatasetIndexNotReady,
    FailedToUpdateTaskStatusTemporally,
    FailedtoCreateTask,
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
    ResultType,
    ResultState,
)
from app.config import settings
from app import schemas, crud, models
from app.libs.models import create_model_stages
from app.utils.cache import CacheClient
from app.utils.ymir_controller import ControllerClient, gen_task_hash
from app.utils.ymir_viz import VizClient
from common_utils.labels import UserLabels


class Retry(Exception):
    pass


async def should_retry(resp: aiohttp.ClientResponse) -> bool:
    if not resp.ok:
        # server returned 500, for example
        return True
    response = await resp.json()
    if int(response["code"]) == FailedToUpdateTaskStatusTemporally.code:
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
        normalized["class_ids"] = user_labels.id_for_names(names=parameters.keywords, raise_if_unknown=True)[0]

    if parameters.preprocess:
        normalized["preprocess"] = parameters.preprocess.json()
    return normalized


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

    logger.info("[create task] created task name: %s", task_info.name)
    if args.get("class_ids"):
        try:
            viz_client = VizClient()
            viz_client.initialize(user_id=user_id, project_id=task_in.project_id)
            viz_client.send_metrics(
                metrics_group="task",
                id=task_info.hash,
                create_time=int(task_info.create_datetime.timestamp()),
                keyword_ids=args["class_ids"],
            )
        except Exception:
            logger.exception(
                "[create task] failed to write task(%s) stats to viewer, continue anyway",
                task.hash,
            )
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
        )
        self.cache = CacheClient(user_id=self.user_id)

        self._result: Optional[Dict] = None

    @cached_property
    def user_labels(self) -> Dict:
        return self.controller.get_labels_of_user(self.user_id)

    @cached_property
    def model_info(self) -> Optional[Dict]:
        try:
            result = self.viz.get_model_info(self.task_hash)
        except (ModelNotReady, ModelNotFound):
            logger.exception("[update task] failed to get model_info: model not ready")
            return None
        except Exception:
            logger.exception("[update task] failed to get model_info: unknown error")
            return None
        else:
            logger.info(f"[viewer_model] model_info: {result}")
            return result

    @cached_property
    def dataset_info(self) -> Optional[Dict]:
        try:
            dataset_info = self.viz.get_dataset_info(
                self.task_hash, user_labels=self.user_labels, check_index_status=True
            )
        except DatasetIndexNotReady:
            raise FailedToUpdateTaskStatusTemporally()
        except Exception:
            logger.exception("[update task] failed to get dataset_info, check viz log")
            return None
        if dataset_info["new_types_added"]:
            logger.info("[update task] delete user keywords cache for new keywords from dataset")
            self.cache.delete_personal_keywords_cache()
        return dataset_info

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
        """
        task_result: task update from monitor
        task_in_db: is required to add back model config to task
        """
        if self.result_type is ResultType.dataset:
            self.update_dataset_result(task_result)
        elif self.result_type is ResultType.model:
            self.update_model_result(task_result, task_in_db)

    def update_model_result(self, task_result: schemas.TaskUpdateStatus, task_in_db: models.Task) -> None:
        """
        Criterion for ready model: viewer returns valid model_info
        """
        model_record = crud.model.get_by_task_id(self.db, task_id=self.task.id)
        if not model_record:
            logger.error("[update task] task result (model) not found, skip")
            return
        model_info = self.model_info
        if model_info:
            # as long as model info is ready, regardless of task status, just set model as ready
            crud.task.update_parameters_and_config(
                self.db,
                task=task_in_db,
                parameters=model_info["task_parameters"],
                config=json.dumps(model_info["executor_config"]),
            )
            crud.model.finish(self.db, model_record.id, result_state=ResultState.ready, result=model_info)
            create_model_stages(self.db, model_record.id, model_info)
        else:
            crud.model.finish(self.db, model_record.id, result_state=ResultState.error)

    def update_dataset_result(self, task_result: schemas.TaskUpdateStatus) -> None:
        """
        Criterion for ready dataset: task state is DONE and viewer returns valid dataset_info
        """
        dataset_record = crud.dataset.get_by_task_id(self.db, task_id=self.task.id)
        if not dataset_record:
            logger.error("[update task] task result (dataset) not found, skip")
            return
        if task_result.state is TaskState.done and self.dataset_info:
            crud.dataset.finish(
                self.db,
                dataset_record.id,
                result_state=ResultState.ready,
                result=self.dataset_info,
            )
        else:
            crud.dataset.finish(
                self.db,
                dataset_record.id,
                result_state=ResultState.error,
            )
