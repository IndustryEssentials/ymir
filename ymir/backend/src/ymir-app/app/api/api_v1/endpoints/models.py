import enum
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateModelError,
    InvalidConfiguration,
    ModelNotFound,
)
from app.config import settings
from app.constants.state import TaskType, ResultState
from app.utils.files import save_file

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


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"
    map = "map"


@router.get("/", response_model=schemas.ModelPaginationOut)
def list_models(
    db: Session = Depends(deps.get_db),
    name: str = Query(None, description="search by model's name"),
    state: ResultState = Query(None),
    project_id: int = Query(None),
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
    - name
    - state
    - project_id
    - start_time, end_time
    """
    models, total = crud.model.get_multi_models(
        db,
        user_id=current_user.id,
        project_id=project_id,
        name=name,
        state=state,
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
    "/",
    response_model=schemas.ModelOut,
)
def import_model(
    *,
    db: Session = Depends(deps.get_db),
    model_import: schemas.ModelImport,
    current_user: models.User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks,
) -> Any:

    # 1. validation
    if crud.model.is_duplicated_name(db, user_id=current_user.id, name=model_import.name):
        raise DuplicateModelError()
    if not settings.MODELS_PATH:
        # fixme
        #  adhoc put model file to underlying storage directly
        raise InvalidConfiguration()

    # 2. create placeholder task
    task = crud.task.create_placeholder(
        db,
        type_=TaskType.import_data,
        user_id=current_user.id,
        project_id=model_import.project_id,
    )
    logger.info("[import model] related task created: %s", task.hash)

    # 3. create model record
    model = create_model_record(db, model_import, task)
    logger.info("[import model] model record created: %s", model)

    # 4. run background task
    storage_path = settings.MODELS_PATH
    background_tasks.add_task(import_model_in_background, model_import.input_url, model.hash, storage_path)
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


def import_model_in_background(model_url: str, model_hash: str, storage_path: str) -> None:
    logger.info(
        "[import model] start importing model file from %s, save to %s",
        model_url,
        storage_path,
    )
    save_file(model_url, storage_path, model_hash)


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


@router.patch(
    "/{model_id}",
    response_model=schemas.ModelOut,
    responses={404: {"description": "Model Not Found"}},
)
def update_model_name(
    *,
    db: Session = Depends(deps.get_db),
    model_id: int = Path(..., example="12"),
    model_in: schemas.ModelUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update model name
    """
    model = crud.model.get_by_user_and_name(db, user_id=current_user.id, name=model_in.name)
    if model:
        raise DuplicateModelError()

    model = crud.model.get(db, id=model_id)
    if not model:
        raise ModelNotFound()
    model = crud.model.update(db, db_obj=model, obj_in=model_in)
    return {"result": model}
