import enum
from typing import Any

from fastapi import APIRouter, Depends, Query, Path
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DatasetGroupNotFound,
    DuplicateDatasetGroupError,
)
from app.utils.ymir_controller import ControllerClient

router = APIRouter()


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"


@router.get("/", response_model=schemas.DatasetGroupPaginationOut)
def list_dataset_groups(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Query(None, description="search by dataset group name"),
    project_id: int = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: SortField = Query(SortField.id),
    is_desc: bool = Query(True),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
) -> Any:
    dataset_groups, total = crud.dataset_group.get_multi_dataset_groups(
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
    return {"result": {"total": total, "items": dataset_groups}}


@router.post("/", response_model=schemas.DatasetGroupOut)
def create_dataset_group(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    obj_in: schemas.DatasetGroupCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Create dataset group
    """
    if crud.dataset_group.is_duplicated_name_in_project(db, project_id=obj_in.project_id, name=obj_in.name):
        raise DuplicateDatasetGroupError()
    dataset_group = crud.dataset_group.create_with_user_id(db, user_id=current_user.id, obj_in=obj_in)
    logger.info("[create datasetgroup] dataset group record created: %s", dataset_group)
    return {"result": dataset_group}


@router.get(
    "/{group_id}",
    response_model=schemas.DatasetGroupOut,
)
def get_dataset_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a dataset group detail
    """
    dataset_group = crud.dataset_group.get(db, id=group_id)
    if not dataset_group:
        raise DatasetGroupNotFound()
    return {"result": dataset_group}


@router.patch(
    "/{group_id}",
    response_model=schemas.DatasetGroupOut,
)
def update_dataset_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: int = Path(...),
    obj_update: schemas.DatasetGroupUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change dataset group name
    """
    dataset_group = crud.dataset_group.get_by_user_and_id(db, user_id=current_user.id, id=group_id)
    if not dataset_group:
        raise DatasetGroupNotFound()

    if crud.dataset_group.is_duplicated_name_in_project(db, project_id=dataset_group.project_id, name=obj_update.name):
        raise DuplicateDatasetGroupError()

    dataset_group = crud.dataset_group.update(db, db_obj=dataset_group, obj_in=obj_update)
    return {"result": dataset_group}


@router.delete(
    "/{group_id}",
    response_model=schemas.DatasetGroupOut,
)
def delete_dataset_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete dataset group
    (soft delete actually)
    """
    dataset_group = crud.dataset_group.get(db, id=group_id)
    if not dataset_group:
        raise DatasetGroupNotFound()

    crud.dataset.remove_group_resources(db, group_id=group_id)
    dataset_group = crud.dataset_group.soft_remove(db, id=group_id)
    return {"result": dataset_group}
