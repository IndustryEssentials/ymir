import enum
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    ModelNotFound,
    DuplicateModelGroupError,
    FailedtoImportModel,
    FailedToHideProtectedResources,
    RefuseToProcessMixedOperations,
    ProjectNotFound,
)
from app.constants.state import TaskState, TaskType, ResultState
from app.utils.ymir_controller import ControllerClient
from app.libs.models import import_model_in_background

router = APIRouter()


@router.get(
    "/batch",
    response_model=schemas.ModelsOut,
)
def batch_get_models(
    db: Session = Depends(deps.get_db),
    model_ids: str = Query(None, alias="ids"),
) -> Any:
    ids = [int(i) for i in model_ids.split(",")]
    models = crud.model.get_multi_by_ids(db, ids=ids)
    return {"result": models}


@router.post(
    "/batch",
    response_model=schemas.ModelsOut,
)
def batch_update_models(
    *,
    db: Session = Depends(deps.get_db),
    model_ops: schemas.BatchOperations,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    project = crud.project.get(db, model_ops.project_id)
    if not project:
        raise ProjectNotFound()
    to_process = {op.id_ for op in model_ops.operations}
    if to_process.intersection(project.referenced_model_ids):
        raise FailedToHideProtectedResources()
    actions = {op.action for op in model_ops.operations}
    if len(actions) != 1:
        raise RefuseToProcessMixedOperations()

    models = crud.model.batch_toggle_visibility(db, ids=list(to_process), action=list(actions)[0])
    return {"result": models}


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"
    update_datetime = "update_datetime"
    map = "map"
    source = "source"


@router.get("/", response_model=schemas.ModelPaginationOut)
def list_models(
    db: Session = Depends(deps.get_db),
    source: TaskType = Query(None, description="type of related task"),
    state: ResultState = Query(None),
    project_id: int = Query(None),
    group_id: int = Query(None),
    visible: bool = Query(True),
    training_dataset_id: int = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: SortField = Query(SortField.id),
    is_desc: bool = Query(True),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of models

    pagination is supported by means of offset and limit

    filters:
    - state
    - project_id
    - start_time, end_time
    """
    models, total = crud.model.get_multi_models(
        db,
        user_id=current_user.id,
        project_id=project_id,
        group_id=group_id,
        source=source,
        state=state,
        visible=visible,
        offset=offset,
        limit=limit,
        order_by=order_by.name,
        is_desc=is_desc,
        start_time=start_time,
        end_time=end_time,
    )
    payload = {"total": total, "items": models}
    return {"result": payload}


@router.post(
    "/importing",
    response_model=schemas.ModelOut,
)
def import_model(
    *,
    db: Session = Depends(deps.get_db),
    model_import: schemas.ModelImport,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    background_tasks: BackgroundTasks,
) -> Any:

    # 1. validation model group name
    if crud.model_group.is_duplicated_name_in_project(
        db=db, project_id=model_import.project_id, name=model_import.group_name
    ):
        raise DuplicateModelGroupError()

    # 2. create placeholder task
    if model_import.import_type is None:
        raise FailedtoImportModel
    task = crud.task.create_placeholder(
        db=db,
        type_=model_import.import_type,
        state_=TaskState.pending,
        user_id=current_user.id,
        project_id=model_import.project_id,
    )
    logger.info("[import model] related task created: %s", task.hash)

    # 3. create model group
    model_group_in = schemas.ModelGroupCreate(
        name=model_import.group_name,
        project_id=model_import.project_id,
        description=model_import.description,
    )
    model_group = crud.model_group.create_with_user_id(db=db, user_id=current_user.id, obj_in=model_group_in)

    # 4. create model record
    model_in = schemas.ModelCreate(
        description=model_import.description,
        source=task.type,
        result_state=ResultState.processing,
        model_group_id=model_group.id,
        project_id=model_import.project_id,
        user_id=current_user.id,
        task_id=task.id,
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in, dest_group_name=model_import.group_name)
    logger.info("[import model] model record created: %s", model)

    # 5. run background task
    background_tasks.add_task(
        import_model_in_background,
        db,
        controller_client,
        model_import,
        current_user.id,
        task.hash,
        model.id,
    )
    return {"result": model}


def create_model_record(db: Session, model_import: schemas.ModelImport, task: models.Task) -> models.Model:
    """
    bind task info to model record
    """
    model_info = jsonable_encoder(model_import)
    model_info.update(
        {
            "hash": task.hash,
            "task_id": task.id,
            "user_id": task.user_id,
        }
    )
    return crud.model.create(db, obj_in=schemas.ModelCreate(**model_info))


@router.delete(
    "/{model_id}",
    response_model=schemas.ModelOut,
    responses={
        400: {"description": "No permission"},
        404: {"description": "Model Not Found"},
    },
)
def delete_model(
    *,
    db: Session = Depends(deps.get_db),
    model_id: int = Path(..., example="12"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete model
    (soft delete actually)
    """
    model = crud.model.get_by_user_and_id(db, user_id=current_user.id, id=model_id)
    if not model:
        raise ModelNotFound()

    model = crud.model.soft_remove(db, id=model_id)
    return {"result": model}


@router.get(
    "/{model_id}",
    response_model=schemas.ModelOut,
    responses={404: {"description": "Model Not Found"}},
)
def get_model(
    db: Session = Depends(deps.get_db),
    model_id: int = Path(..., example="12"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get verbose information of specific model
    """
    model = crud.model.get_by_user_and_id(db, user_id=current_user.id, id=model_id)
    if not model:
        raise ModelNotFound()
    return {"result": model}
