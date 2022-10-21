import enum
from typing import Any
import uuid

from fastapi import APIRouter, Depends, Path, Query, BackgroundTasks
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    ProjectNotFound,
    DuplicateProjectError,
    FailedToCreateProject,
    NoDatasetPermission,
    DatasetNotFound,
)
from app.config import settings
from app.constants.state import ResultState, RunningStates, TaskType, TrainingType
from app.utils.cache import CacheClient
from app.utils.ymir_controller import ControllerClient, gen_task_hash
from app.libs.projects import setup_sample_project_in_background, send_project_metrics
from app.libs.labels import ensure_labels_exist
from common_utils.labels import UserLabels

router = APIRouter()


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"


@router.get("/", response_model=schemas.ProjectPaginationOut)
def list_projects(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Query(None),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: SortField = Query(SortField.id),
    is_desc: bool = Query(True),
) -> Any:
    """
    Get projects list

    filter:
    - name

    order_by:
    - id
    - create_datetime
    """
    projects, total = crud.project.get_multi_projects(
        db,
        user_id=current_user.id,
        name=name,
        offset=offset,
        limit=limit,
        order_by=order_by.name,
        is_desc=is_desc,
        start_time=start_time,
        end_time=end_time,
    )

    return {"result": {"total": total, "items": projects}}


@router.post("/samples", response_model=schemas.ProjectOut)
def create_sample_project(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    background_tasks: BackgroundTasks,
    cache: CacheClient = Depends(deps.get_cache),
) -> Any:
    """
    Create sample project
    """
    project_name = f"sample_project_{uuid.uuid4().hex[:8]}"
    project_in = schemas.ProjectCreate(
        name=project_name,
        training_keywords=settings.SAMPLE_PROJECT_KEYWORDS,
        chunk_size=2,
        is_example=True,
    )
    project = crud.project.create_project(db, user_id=current_user.id, obj_in=project_in)
    project_task_hash = gen_task_hash(current_user.id, project.id)
    training_class_ids = ensure_labels_exist(
        user_id=current_user.id,
        user_labels=user_labels,
        controller_client=controller_client,
        keywords=settings.SAMPLE_PROJECT_KEYWORDS,
        cache=cache,
    )

    try:
        controller_client.create_project(
            user_id=current_user.id,
            project_id=project.id,
            task_id=project_task_hash,
        )
    except ValueError:
        crud.project.soft_remove(db, id=project.id)
        raise FailedToCreateProject()

    send_project_metrics(
        current_user.id,
        project.id,
        project.name,
        training_class_ids,
        TrainingType(project.training_type).name,
        int(project.create_datetime.timestamp()),
    )

    background_tasks.add_task(
        setup_sample_project_in_background,
        db,
        controller_client,
        project_name=project.name,
        project_id=project.id,
        user_id=current_user.id,
        project_task_hash=project_task_hash,
    )
    return {"result": project}


@router.post("/", response_model=schemas.ProjectOut)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_in: schemas.ProjectCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Create project
    """
    if crud.project.is_duplicated_name(db, user_id=current_user.id, name=project_in.name):
        raise DuplicateProjectError()

    # 1.create project to get task_id for sending to controller
    project = crud.project.create_project(db, user_id=current_user.id, obj_in=project_in)

    task_id = gen_task_hash(current_user.id, project.id)

    # 2.send to controller
    try:
        resp = controller_client.create_project(
            user_id=current_user.id,
            project_id=project.id,
            task_id=task_id,
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        crud.project.soft_remove(db, id=project.id)
        raise FailedToCreateProject()

    if project_in.enable_iteration:
        # 3.create task info
        task = crud.task.create_placeholder(
            db, type_=TaskType.create_project, user_id=current_user.id, project_id=project.id
        )

        # 3.create dataset group to build dataset info
        dataset_name = f"{project_in.name}_training_dataset"
        dataset_paras = schemas.DatasetGroupCreate(name=dataset_name, project_id=project.id, user_id=current_user.id)
        dataset_group = crud.dataset_group.create_with_user_id(db, user_id=current_user.id, obj_in=dataset_paras)

        # 4.create init dataset
        dataset_in = schemas.DatasetCreate(
            name=dataset_name,
            hash=task_id,
            dataset_group_id=dataset_group.id,
            project_id=project.id,
            user_id=current_user.id,
            source=task.type,
            result_state=ResultState.ready,
            task_id=task.id,
        )
        initial_dataset = crud.dataset.create_with_version(db, obj_in=dataset_in)

        # 5.update project info
        project = crud.project.update_resources(
            db,
            project_id=project.id,
            project_update=schemas.ProjectUpdate(
                training_dataset_group_id=dataset_group.id, initial_training_dataset_id=initial_dataset.id
            ),
        )

    send_project_metrics(
        current_user.id,
        project.id,
        project.name,
        user_labels.id_for_names(names=project_in.training_keywords, raise_if_unknown=True)[0],
        TrainingType(project.training_type).name,
        int(project.create_datetime.timestamp()),
    )

    logger.info("[create project] project record created: %s", project)
    return {"result": project}


@router.get(
    "/{project_id}",
    response_model=schemas.ProjectOut,
)
def get_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a project detail
    """
    project = crud.project.get_by_user_and_id(db, user_id=current_user.id, id=project_id)
    if not project:
        raise ProjectNotFound()
    return {"result": project}


@router.patch(
    "/{project_id}",
    response_model=schemas.ProjectOut,
)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int = Path(...),
    project_update: schemas.ProjectUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Setting up a project
    """
    project = crud.project.get_by_user_and_id(db, user_id=current_user.id, id=project_id)
    if not project:
        raise ProjectNotFound()
    if project_update.initial_training_dataset_id is not None:
        dataset = crud.dataset.get(db, id=project_update.initial_training_dataset_id)
        if not dataset:
            raise DatasetNotFound()
        if project.training_dataset_group_id != dataset.dataset_group_id:
            raise NoDatasetPermission()
    if project_update.name and crud.project.is_duplicated_name(db, user_id=current_user.id, name=project_update.name):
        raise DuplicateProjectError()
    project = crud.project.update_resources(db, project_id=project.id, project_update=project_update)

    return {"result": project}


@router.delete(
    "/{project_id}",
    response_model=schemas.ProjectOut,
)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int = Path(...),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete project, and terminate all tasks
    """
    project = crud.project.get_by_user_and_id(db, user_id=current_user.id, id=project_id)
    if not project:
        raise ProjectNotFound()

    project = crud.project.soft_remove(db, id=project_id)

    unfinished_tasks = crud.task.get_tasks_by_states(
        db,
        states=RunningStates,
        including_deleted=True,
        project_id=project_id,
    )
    for task in unfinished_tasks:
        try:
            controller_client.terminate_task(user_id=current_user.id, task_hash=task.hash, task_type=task.type)
        except Exception:
            logger.info(f"Failed to terminate task: {task.hash} of project_id: {project_id}")
            continue

    return {"result": project}


@router.get(
    "/{project_id}/status",
    response_model=schemas.project.ProjectStatusOut,
)
def check_project_status(
    *,
    project_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Check if current project is dirty
    """
    is_clean = controller_client.check_repo_status(user_id=current_user.id, project_id=project_id)
    return {"result": {"is_dirty": not is_clean}}
