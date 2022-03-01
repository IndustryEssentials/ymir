import enum
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    ProjectNotFound,
    DuplicateProjectError,
)
from app.utils.ymir_controller import ControllerClient

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
    current_user: models.User = Depends(deps.get_current_active_admin),
    project_in: schemas.ProjectCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create project
    """
    if crud.project.is_duplicated_name(
        db, user_id=current_user.id, name=project_in.name
    ):
        raise DuplicateProjectError()
    project = crud.project.create_with_user_id(
        db, user_id=current_user.id, obj_in=project_in
    )

    # todo
    # call controller
    # create dataset_group info

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
    # todo : get dataset name , get dataset count
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
    project = crud.project.get_by_user_and_id(
        db, user_id=current_user.id, id=project_id
    )
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
    current_user: models.User = Depends(deps.get_current_active_admin),
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
