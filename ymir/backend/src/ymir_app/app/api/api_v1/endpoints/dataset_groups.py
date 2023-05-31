from typing import Any

from fastapi import APIRouter, Depends, Query, Path
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import (
    DatasetGroupNotFound,
    DuplicateDatasetGroupError,
)
from app.utils.ymir_controller import ControllerClient

router = APIRouter()


@router.get("/", response_model=schemas.DatasetGroupPaginationOut)
def list_dataset_groups(
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    name: str = Query(None, description="search by dataset group name"),
    project_id: int = Query(None),
    pagination: schemas.CommonPaginationParams = Depends(),
) -> Any:
    dataset_groups, total = crud.dataset_group.get_multi_dataset_groups(
        db,
        user_id=current_user.id,
        project_id=project_id,
        name=name,
        pagination=pagination,
    )
    return {"result": {"total": total, "items": dataset_groups}}


@router.post("/", response_model=schemas.DatasetGroupOut)
def create_dataset_group(
    *,
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
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


@router.post("/check_names", response_model=schemas.dataset_group.DatasetGroupNamesOut)
def check_duplicated_dataset_group_names(
    *,
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    in_group_names: schemas.dataset_group.DatasetGroupNamesWithProject,
) -> Any:
    """
    Check if given dataset_group names exist in the same project
    """
    project_id, names = in_group_names.project_id, in_group_names.names
    duplicated_groups = crud.dataset_group.get_multi_by_project_and_names(db, project_id=project_id, names=names)
    duplicated_names = [group.name for group in duplicated_groups]
    return {"result": {"names": duplicated_names}}


@router.get(
    "/{group_id}",
    response_model=schemas.DatasetGroupOut,
)
def get_dataset_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: int = Path(...),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
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
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
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
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
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
