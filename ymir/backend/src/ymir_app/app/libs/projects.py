from typing import Optional, List
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.constants.state import ResultState, TaskType, TaskState
from app.utils.ymir_controller import ControllerClient
from app.utils.ymir_viz import VizClient
from app.libs.datasets import import_dataset_in_background
from app.libs.models import import_model_in_background


def setup_dataset_and_group(
    db: Session,
    controller_client: ControllerClient,
    group_name: str,
    project_id: int,
    user_id: int,
    task_type: TaskType,
    task_hash: Optional[str] = None,
    input_url: Optional[str] = None,
    result_state: Optional[ResultState] = ResultState.processing,
) -> models.Dataset:
    task_state = TaskState.done if result_state is ResultState.ready else TaskState.pending
    task = crud.task.create_placeholder(db, type_=task_type, state_=task_state, user_id=user_id, project_id=project_id)
    task_hash = task_hash or task.hash
    dataset_group = crud.dataset_group.create_with_user_id(
        db, user_id=user_id, obj_in=schemas.DatasetGroupCreate(name=group_name, project_id=project_id, user_id=user_id)
    )
    dataset = crud.dataset.create_with_version(
        db,
        obj_in=schemas.DatasetCreate(
            hash=task_hash,
            dataset_group_id=dataset_group.id,
            project_id=project_id,
            result_state=result_state,
            user_id=user_id,
            source=task.type,
            task_id=task.id,
        ),
    )
    if input_url:
        dataset_import = schemas.DatasetImport(group_name=group_name, project_id=project_id, input_url=input_url)
        import_dataset_in_background(db, controller_client, dataset_import, user_id, task_hash, dataset.id)
    return dataset


def setup_model_and_group(
    db: Session,
    controller_client: ControllerClient,
    group_name: str,
    project_id: int,
    user_id: int,
    task_hash: Optional[str] = None,
    input_url: Optional[str] = None,
    task_type: TaskType = TaskType.import_model,
    result_state: Optional[ResultState] = ResultState.processing,
) -> models.Model:
    task = crud.task.create_placeholder(
        db=db,
        type_=task_type,
        state_=TaskState.pending,
        user_id=user_id,
        project_id=project_id,
    )
    task_hash = task_hash or task.hash
    logger.info("[sample project] import model related task created: %s", task.hash)

    model_group_in = schemas.ModelGroupCreate(name=group_name, project_id=project_id)
    model_group = crud.model_group.create_with_user_id(db=db, user_id=user_id, obj_in=model_group_in)

    model_in = schemas.ModelCreate(
        source=task.type,
        result_state=result_state,
        model_group_id=model_group.id,
        project_id=project_id,
        user_id=user_id,
        task_id=task.id,
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    if input_url:
        model_import = schemas.ModelImport(group_name=group_name, project_id=project_id, input_url=input_url)
        import_model_in_background(db, controller_client, model_import, user_id, task_hash, model.id)
    return model


def setup_sample_project_in_background(
    db: Session,
    controller_client: ControllerClient,
    project_name: str,
    project_id: int,
    user_id: int,
    project_task_hash: str,
) -> None:
    # training dataset created by project itself
    training_dataset = setup_dataset_and_group(
        db=db,
        controller_client=controller_client,
        group_name=f"{project_name}_training_dataset",
        project_id=project_id,
        user_id=user_id,
        task_hash=project_task_hash,
        task_type=TaskType.create_project,
        result_state=ResultState.ready,
    )

    # import testing dataset
    validation_dataset = setup_dataset_and_group(
        db=db,
        controller_client=controller_client,
        group_name=f"{project_name}_validation_dataset",
        project_id=project_id,
        user_id=user_id,
        task_type=TaskType.import_data,
        input_url=settings.SAMPLE_PROJECT_VALIDATION_DATASET_URL,
    )

    # import mining dataset
    mining_dataset = setup_dataset_and_group(
        db=db,
        controller_client=controller_client,
        group_name=f"{project_name}_mining_dataset",
        project_id=project_id,
        user_id=user_id,
        task_type=TaskType.import_data,
        input_url=settings.SAMPLE_PROJECT_MINING_DATASET_URL,
    )

    # import model
    model = setup_model_and_group(
        db=db,
        controller_client=controller_client,
        group_name=f"{project_name}_model",
        project_id=project_id,
        user_id=user_id,
        input_url=settings.SAMPLE_PROJECT_MODEL_URL,
    )

    crud.project.update_resources(
        db,
        project_id=project_id,
        project_update=schemas.ProjectUpdate(
            training_dataset_group_id=training_dataset.dataset_group_id,
            initial_training_dataset_id=training_dataset.id,
            validation_dataset_id=validation_dataset.id,
            mining_dataset_id=mining_dataset.id,
            initial_model_id=model.id,
        ),
    )


def send_project_metrics(
    user_id: int,
    project_id: int,
    project_name: str,
    keyword_ids: List[int],
    project_type: str,
    create_time: int,
) -> None:
    try:
        viz_client = VizClient()
        viz_client.initialize(user_id=user_id, project_id=project_id)
        viz_client.send_metrics(
            metrics_group="project",
            id=f"{project_id:0>6}",
            create_time=create_time,
            keyword_ids=keyword_ids,
            extra_data={"project_type": project_type},
        )
    except Exception:
        logger.exception(
            "[metrics] failed to send project(%s) stats to viewer, continue anyway",
            project_name,
        )
