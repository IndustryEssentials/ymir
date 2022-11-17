from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateIterationError,
    IterationNotFound,
    ProjectNotFound,
    TaskNotFound,
    IterationStepNotFound,
    IterationStepHasFinished,
)
from app.crud.crud_iteration_step import StepNotFound
from app.libs.iterations import calculate_mining_progress
from app.libs.iteration_steps import initialize_steps, backfill_iteration_slots

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
    project = crud.project.get(db, obj_in.project_id)
    if not project:
        raise ProjectNotFound()
    previous_iteration = project.current_iteration

    if previous_iteration and previous_iteration.previous_iteration == obj_in.previous_iteration:
        raise DuplicateIterationError()

    iteration = crud.iteration.create_with_user_id(db, user_id=current_user.id, obj_in=obj_in)
    logger.info("[create iteration] iteration record created: %s", iteration)
    initialize_steps(db, iteration.id, project, previous_iteration)
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


@router.get("/{iteration_id}/steps", response_model=schemas.IterationStepsOut)
def list_iteration_steps(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    iteration = crud.iteration.get_by_user_and_id(db, user_id=current_user.id, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    steps = crud.iteration_step.get_multi_by_iteration(db, iteration_id=iteration_id)
    return {"result": steps}


@router.get("/{iteration_id}/steps/{step_id}", response_model=schemas.IterationStepOut)
def get_iteration_step(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    step_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    iteration = crud.iteration.get_by_user_and_id(db, user_id=current_user.id, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    step = crud.iteration_step.get(db, step_id)
    if not step:
        raise IterationStepNotFound()
    return {"result": step}


@router.post("/{iteration_id}/steps/{step_id}/bind", response_model=schemas.IterationStepOut)
def bind_iteration_step(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    step_id: int = Path(...),
    task_id: int = Query(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    start given step:
    1. bind existing task to given step
    2. record task result and record dataset_id or model_id in step record
    """
    iteration = crud.iteration.get_by_user_and_id(db, user_id=current_user.id, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    step = crud.iteration_step.get(db, id=step_id)
    if not step:
        raise IterationStepNotFound()
    if step.is_finished:
        raise IterationStepHasFinished()

    task_in_db = crud.task.get(db, task_id)
    if not task_in_db:
        raise TaskNotFound()
    step = crud.iteration_step.bind_task(db, id=step_id, task_id=task_id)
    return {"result": step}


@router.post("/{iteration_id}/steps/{step_id}/unbind", response_model=schemas.IterationStepOut)
def unbind_iteration_step(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    step_id: int = Path(...),
    user_labels: UserLabels = Depends(deps.get_user_labels),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    iteration = crud.iteration.get_by_user_and_id(db, user_id=current_user.id, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    step = crud.iteration_step.get(db, id=step_id)
    if not step:
        raise IterationStepNotFound()
    if step.is_finished:
        raise IterationStepHasFinished()
    step = crud.iteration_step.unbind_task(db, id=step_id)
    return {"result": step}


@router.post("/{iteration_id}/steps/{step_id}/finish", response_model=schemas.IterationStepOut)
def finish_iteration_step(
    *,
    db: Session = Depends(deps.get_db),
    iteration_id: int = Path(...),
    step_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # make sure iteration belongs to user
    iteration = crud.iteration.get_by_user_and_id(db, user_id=current_user.id, id=iteration_id)
    if not iteration:
        raise IterationNotFound()
    step = crud.iteration_step.get(db, id=step_id)
    if not step:
        raise IterationStepNotFound()
    if step.is_finished:
        raise IterationStepHasFinished()

    try:
        step_result = crud.iteration_step.get_ready_result(db, id=step_id)
        if step_result:
            backfill_iteration_slots(db, step.iteration_id, step.name, step.result.id)  # type: ignore
            next_step = crud.iteration_step.get_next_step(db, id=step_id)
            if next_step:
                logger.info("[finish step] update next step presetting with current step result: %s", step_result)
                crud.iteration_step.update_presetting(db, next_step.id, step_result)
        if step.task:
            logger.info("[finish step] update current step presetting with task parameter")
            crud.iteration_step.update_presetting(db, step_id, step.task.task_parameters)
        step = crud.iteration_step.finish(db, id=step_id)
    except StepNotFound:
        raise IterationStepNotFound()
    return {"result": step}
