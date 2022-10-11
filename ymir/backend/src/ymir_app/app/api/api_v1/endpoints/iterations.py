from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import IterationNotFound
from app.libs.iterations import calculate_mining_progress
from app.libs.iteration_steps import initialize_steps
from app.libs.tasks import create_single_task

from common_utils.labels import UserLabels

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
    initialize_steps(db, iteration.id)
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


@router.get("/{iteration_id}/mining_progress", response_model=schemas.iteration.IterationMiningProgressOut)
def get_mining_progress_of_iteration(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    iteration_id: int = Path(...),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get mining progress of specific iteration
    """
    stats = calculate_mining_progress(db, user_labels, current_user.id, project_id, iteration_id)
    return {"result": stats}


@router.get(
    "/{iteration_id}/steps",
    response_model=schemas.IterationStepsOut,
)
def list_iteration_steps(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    steps = crud.iteration_step.get_multi_by_iteration(db, iteration_id=iteration_id)
    return {"result": steps}


@router.post(
    "/{iteration_id}/steps/{step_id}/start",
    response_model=schemas.IterationStepOut,
)
def start_iteration_step(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    step_id: int = Path(...),
    task_in: schemas.TaskCreate,
    user_labels: UserLabels = Depends(deps.get_user_labels),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    start given step:
    1. create task and record task_id in step record
    2. record task result and record dataset_id or model_id in step record
    """
    task_in_db = create_single_task(db, current_user.id, user_labels, task_in)
    task = schemas.Task.from_orm(task_in_db)
    result_model_id = task.result_model.id if task.result_model else None
    result_dataset_id = task.result_dataset.id if task.result_dataset else None
    step = crud.iteration_step.record_result(
        db, id=step_id, task_id=task_in_db.id, result_model_id=result_model_id, result_dataset_id=result_dataset_id
    )
    return {"result": step}


@router.post(
    "/{iteration_id}/steps/{step_id}/finish",
    response_model=schemas.IterationStepOut,
)
def finish_iteration_step(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    step_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    step = crud.iteration_step.finish(db, id=step_id)
    return {"result": step}
