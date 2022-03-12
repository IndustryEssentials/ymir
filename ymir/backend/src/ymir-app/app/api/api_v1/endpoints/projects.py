import enum
from typing import Any, Dict

from fastapi import APIRouter, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    ProjectNotFound,
    DuplicateProjectError,
    FailedToCreateProject,
)
from app.constants.state import ResultState
from app.constants.state import TaskType
from app.utils.ymir_controller import ControllerClient, gen_task_hash

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
    personal_labels: Dict = Depends(deps.get_personal_labels),
) -> Any:
    """
    Create project
    """
    if crud.project.is_duplicated_name(db, user_id=current_user.id, name=project_in.name):
        raise DuplicateProjectError()

    # 1.create project to get task_id for sending to controller
    project = crud.project.create_project(db, user_id=current_user.id, obj_in=project_in)

    task_id = gen_task_hash(current_user.id, project.id)

    training_classes = [personal_labels["name_to_id"][keyword]["id"] for keyword in project_in.training_keywords]

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
        result_state=ResultState.ready,
        task_id=task.id,
    )
    crud.dataset.create_with_version(db, obj_in=dataset_in)

    # 5.update project info
    project = crud.project.update(
        db,
        db_obj=project,
        obj_in=schemas.ProjectUpdate(training_dataset_group_id=dataset_group.id),
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
    project = crud.project.get(db, id=project_id)
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
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Setting up a project
    """
    project = crud.project.get_by_user_and_id(db, user_id=current_user.id, id=project_id)
    if not project:
        raise ProjectNotFound()

    project = crud.project.update(db, db_obj=project, obj_in=project_update)
    return {"result": project}


@router.delete(
    "/{project_id}",
    response_model=schemas.ProjectOut,
)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete project
    (soft delete actually)
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise ProjectNotFound()

    project = crud.project.soft_remove(db, id=project_id)
    return {"result": project}
