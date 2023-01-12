from functools import cached_property, partial
import json
import itertools
import asyncio
from typing import Dict, List, Optional, Tuple

import aiohttp
from fastapi.logger import logger
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.errors.errors import (
    ProjectNotFound,
    DatasetIndexNotReady,
    DuplicateDatasetGroupError,
    FailedToUpdateTaskStatusTemporally,
    FailedtoCreateTask,
    ModelNotReady,
    ModelNotFound,
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
from app.libs.datasets import ensure_datasets_are_ready
from app.libs.labels import keywords_to_class_ids
from app.libs.metrics import send_keywords_metrics
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


def create_single_task(db: Session, user_id: int, user_labels: UserLabels, task_in: schemas.TaskCreate) -> models.Task:
    project_getter = partial(crud.project.get, db, task_in.project_id)
    iterations_getter = partial(crud.iteration.get_multi_by_project, db)
    datasets_getter = partial(ensure_datasets_are_ready, db)
    model_stages_getter = partial(crud.model_stage.get_multi_by_ids, db)
    labels_getter = partial(keywords_to_class_ids, user_labels)
    docker_image_getter = partial(crud.docker_image.get, db)

    task_in.fulfill_parameters(
        datasets_getter,
        model_stages_getter,
        iterations_getter,
        labels_getter,
        docker_image_getter,
        project_getter,
    )
    task_hash = gen_task_hash(user_id, task_in.project_id)
    try:
        controller_client = ControllerClient()
        resp = controller_client.create_task(
            user_id=user_id,
            project_id=task_in.project_id,
            task_id=task_hash,
            task_type=task_in.type,
            task_parameters=task_in.parameters.dict(),
            archived_task_parameters=task_in.parameters.json(),
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        logger.exception("[create task] controller error")
        raise FailedtoCreateTask()
    except KeyError:
        logger.exception("[create task] parameter check failed")
        raise RequiredFieldMissing()

    task = crud.task.create_task(db, obj_in=task_in, task_hash=task_hash, user_id=user_id)
    task_result = TaskResult(db, task)
    task_result.create(
        task_in.parameters.dataset_id,
        task_in.parameters.dataset_group_id,
        task_in.parameters.dataset_group_name,
        task_in.parameters.description,
    )

    logger.info("[create task] created task hash: %s", task_hash)
    if task_in.parameters.typed_labels:
        send_keywords_metrics(
            user_id,
            task_in.project_id,
            task_hash,
            [label.class_id for label in task_in.parameters.typed_labels],
            int(task.create_datetime.timestamp()),
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
    def object_type(self) -> int:
        project = crud.project.get(self.db, self.project_id)
        if not project:
            raise ProjectNotFound()
        return project.object_type

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

    def ensure_dest_model_group_exists(self, dataset_id: int) -> int:
        model_group = crud.model_group.get_from_training_dataset(self.db, training_dataset_id=dataset_id)
        if not model_group:
            model_group = crud.model_group.create_model_group(
                self.db,
                user_id=self.user_id,
                project_id=self.project_id,
                training_dataset_id=dataset_id,
            )
            logger.info("created model_group(%s) based on training_dataset(%s)", model_group.id, dataset_id)
        return model_group.id

    def ensure_dest_dataset_group_exists(
        self, dataset_id: int, dataset_group_id: Optional[int], dataset_group_name: Optional[str]
    ) -> int:
        if dataset_group_id:
            dataset_group = crud.dataset_group.get(self.db, dataset_group_id)
            if not dataset_group:
                raise DatasetGroupNotFound()
        elif dataset_group_name:
            if crud.dataset_group.is_duplicated_name_in_project(
                self.db, project_id=self.project_id, name=dataset_group_name
            ):
                raise DuplicateDatasetGroupError()
            dataset_group = crud.dataset_group.create_dataset_group(
                self.db,
                name=dataset_group_name,
                user_id=self.user_id,
                project_id=self.project_id,
            )
        else:
            # if no extra dataset group info provided, save result to the same group as dataset_id
            dataset = crud.dataset.get(self.db, dataset_id)
            if not dataset:
                logger.error(
                    "Failed to predict dest dataset_group_id from non-existing dataset(%s)",
                    dataset_id,
                )
                raise DatasetNotFound()
            dataset_group = crud.dataset_group.get(self.db, dataset.dataset_group_id)
            if not dataset_group:
                raise DatasetGroupNotFound()
        return dataset_group.id

    def get_dest_group_id(
        self, dataset_id: int, dataset_group_id: Optional[int], dataset_group_name: Optional[str]
    ) -> int:
        if self.result_type is ResultType.dataset:
            return self.ensure_dest_dataset_group_exists(dataset_id, dataset_group_id, dataset_group_name)
        return self.ensure_dest_model_group_exists(dataset_id)

    def create(
        self,
        dataset_id: int,
        dataset_group_id: Optional[int],
        dataset_group_name: Optional[str],
        description: Optional[str] = None,
    ) -> Dict[str, Dict]:
        dest_group_id = self.get_dest_group_id(dataset_id, dataset_group_id, dataset_group_name)
        if self.result_type is ResultType.dataset:
            dataset = crud.dataset.create_as_task_result(self.db, self.task, dest_group_id, description)
            logger.info("[create task] created new dataset(%s) as task result", dataset.name)
            return {"dataset": jsonable_encoder(dataset)}
        elif self.result_type is ResultType.model:
            model = crud.model.create_as_task_result(self.db, self.task, dest_group_id, description)
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
        Criterion for ready model: viewer returns valid model_info and object_type matched with project's
        """
        model_record = crud.model.get_by_task_id(self.db, task_id=self.task.id)
        if not model_record:
            logger.error("[update task] task result (model) not found, skip")
            return
        model_info = self.model_info
        if model_info and model_info.get("object_type") == self.object_type:
            # as long as model info is ready, regardless of task status, just set model as ready
            parameters = model_info["task_parameters"]
            if task_in_db.type == TaskType.import_model:
                parameters = filter_task_parameters_from_imported_model(parameters)
            crud.task.update_parameters_and_config(
                self.db,
                task=task_in_db,
                parameters=parameters,
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


def filter_task_parameters_from_imported_model(serialized_task_parameters: str) -> str:
    """
    for imported model, only a few docker_image related parameters are relevant
    """
    KEPT_PARAMETER_KEYS = ["docker_image", "docker_image_config", "preprocess"]
    task_parameters = json.loads(serialized_task_parameters)
    task_parameters = {k: v for k, v in task_parameters.items() if k in KEPT_PARAMETER_KEYS}
    return json.dumps(task_parameters)
