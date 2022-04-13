import enum
from typing import Any

from fastapi import APIRouter, Depends, Query, Path
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    ModelGroupNotFound,
    DuplicateModelGroupError,
)
from app.utils.ymir_controller import ControllerClient

router = APIRouter()


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"


@router.get("/", response_model=schemas.ModelGroupPaginationOut)
def list_model_groups(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_id: int = Query(None),
    name: str = Query(None, description="search by model's name"),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: SortField = Query(SortField.id),
    is_desc: bool = Query(True),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
) -> Any:
    model_groups, total = crud.model_group.get_multi_model_groups(
        db,
        user_id=current_user.id,
        project_id=project_id,
        name=name,
        offset=offset,
        limit=limit,
        order_by=order_by.name,
        is_desc=is_desc,
        start_time=start_time,
        end_time=end_time,
    )
    return {"result": {"total": total, "items": model_groups}}


@router.post("/", response_model=schemas.ModelGroupOut)
def create_model_group(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    obj_in: schemas.ModelGroupCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Create model group
    """
    if crud.model_group.is_duplicated_name_in_project(db, project_id=obj_in.project_id, name=obj_in.name):
        raise DuplicateModelGroupError()
    model_group = crud.model_group.create_with_user_id(db, user_id=current_user.id, obj_in=obj_in)
    logger.info("[create modelgroup] model group record created: %s", model_group)
    return {"result": model_group}


@router.get(
    "/{group_id}",
    response_model=schemas.ModelGroupOut,
)
def get_model_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a model group detail
    """
    model_group = crud.model_group.get(db, id=group_id)
    if not model_group:
        raise ModelGroupNotFound()
    return {"result": model_group}


@router.patch(
    "/{group_id}",
    response_model=schemas.ModelGroupOut,
)
def update_model_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: int = Path(...),
    obj_update: schemas.ModelGroupUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change model group name
    """
    model_group = crud.model_group.get_by_user_and_id(db, user_id=current_user.id, id=group_id)
    if not model_group:
        raise ModelGroupNotFound()

    model_group = crud.model_group.update(db, db_obj=model_group, obj_in=obj_update)
    return {"result": model_group}


@router.delete(
    "/{group_id}",
    response_model=schemas.ModelGroupOut,
)
def delete_model_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete model group
    (soft delete actually)
    """
    model_group = crud.model_group.get(db, id=group_id)
    if not model_group:
        raise ModelGroupNotFound()

    model_group = crud.model_group.soft_remove(db, id=group_id)
    crud.model.remove_group_resources(db, group_id=group_id)
    return {"result": model_group}
