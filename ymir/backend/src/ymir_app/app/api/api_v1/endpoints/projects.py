import enum
import json
from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    ProjectNotFound,
    DuplicateProjectError,
    FailedToCreateProject,
    FailedToConnectClickHouse,
)
from app.constants.state import ResultState
from app.constants.state import RunningStates
from app.constants.state import TaskType, TrainingType
from app.utils.clickhouse import YmirClickHouse
from app.utils.ymir_controller import ControllerClient, gen_task_hash
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


@router.post("/", response_model=schemas.ProjectOut)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_in: schemas.ProjectCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Create project
    """
    if crud.project.is_duplicated_name(db, user_id=current_user.id, name=project_in.name):
        raise DuplicateProjectError()

    # 1.create project to get task_id for sending to controller
    project = crud.project.create_project(db, user_id=current_user.id, obj_in=project_in)

    task_id = gen_task_hash(current_user.id, project.id)

    training_classes = user_labels.get_class_ids(names_or_aliases=project_in.training_keywords)

    # 2.send to controller
    try:
        resp = controller_client.create_project(
            user_id=current_user.id,
            project_id=project.id,
            task_id=task_id,
            args={"training_classes": training_classes},
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        crud.project.soft_remove(db, id=project.id)
        raise FailedToCreateProject()

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
    crud.dataset.create_with_version(db, obj_in=dataset_in)

    # 5.update project info
    project = crud.project.update_resources(
        db,
        project_id=project.id,
        project_update=schemas.ProjectUpdate(training_dataset_group_id=dataset_group.id),
    )

    try:
        clickhouse.save_project_parameter(
            dt=project.create_datetime,
            user_id=project.user_id,
            id_=project.id,
            name=project.name,
            training_type=TrainingType(project.training_type).name,
            training_keywords=json.loads(project.training_keywords),
        )
    except FailedToConnectClickHouse:
        # clickhouse metric shouldn't block create task process
        logger.exception(
            "[create project metrics] failed to write project(%s) stats to clickhouse, continue anyway",
            project.name,
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
