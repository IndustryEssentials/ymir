from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import IterationNotFound

router = APIRouter()


@router.post("/", response_model=schemas.IterationOut)
def create_iteration(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    obj_in: schemas.IterationCreate,
) -> Any:
    """
    Create iteration
    """
    iteration = crud.iteration.create_with_user_id(db, user_id=current_user.id, obj_in=obj_in)
    logger.info("[create iteration] iteration record created: %s", iteration)
    crud.project.update_current_iteration(db, project_id=obj_in.project_id, iteration_id=iteration.id)
    return {"result": iteration}


@router.get("/", response_model=schemas.IterationsOut)
def list_iterations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
) -> Any:
    """
    Get iterations under specific project
    """
    iterations = crud.iteration.get_multi_by_project(db, project_id=project_id)
    return {"result": iterations}


@router.get("/{iteration_id}", response_model=schemas.IterationOut)
def get_iteration(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    iteration_id: int = Path(...),
) -> Any:
    """
    Get verbose information of specific iteration
    """
    iteration = crud.iteration.get(db, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    return {"result": iteration}


@router.patch(
    "/{iteration_id}",
    response_model=schemas.IterationOut,
)
def update_iteration(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    iteration_updates: schemas.IterationUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change iteration stage and update iteration context when necessary

    available stages:
    - prepare_mining = 0
    - mining = 1
    - label = 2
    - prepare_training = 3
    - training = 4
    """
    iteration = crud.iteration.get_by_user_and_id(db, user_id=current_user.id, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    crud.iteration.update_iteration(db, iteration_id=iteration_id, iteration_update=iteration_updates)
    return {"result": iteration}
