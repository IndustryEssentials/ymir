import enum
import random
import secrets
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateModelError,
    InvalidConfiguration,
    ModelNotFound,
    NoModelPermission,
)
from app.config import settings
from app.constants.state import TaskType
from app.models.task import Task
from app.utils.files import save_file
from app.utils.stats import RedisStats
from app.utils.ymir_controller import ControllerRequest

router = APIRouter()


class ModelSortMethod(enum.IntEnum):
    map = 1
    ref_count = 2


@router.get("/", response_model=schemas.ModelOut)
def list_models(
    db: Session = Depends(deps.get_db),
    model_ids: str = Query(None, example="12,13,14", alias="ids"),
    name: str = Query(None, description="search by model's name"),
    source: TaskType = Query(None, description="the type of related task", example=1),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: Optional[ModelSortMethod] = Query(None),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
    current_user: models.User = Depends(deps.get_current_active_user),
    stats_client: RedisStats = Depends(deps.get_stats_client),
) -> Any:
    """
    Get list of models,
    pagination is supported by means of offset and limit

    order is supported by `order_by`:

    - 1: order_by map
    - 2: order_by ref_count
    """
    if order_by is ModelSortMethod.ref_count:
        ids = [
            model[0]
            for model in stats_client.get_top_models(current_user.id, limit=limit)
        ]
    else:
        ids = [int(i) for i in model_ids.split(",")] if model_ids else []

    models, total = crud.model.get_multi_models(
        db,
        user_id=current_user.id,
        ids=ids,
        name=name,
        task_type=source,
        offset=offset,
        limit=limit,
        order_by="map" if order_by is ModelSortMethod.map else None,
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
    current_workspace: models.Workspace = Depends(deps.get_current_workspace),
    background_tasks: BackgroundTasks,
) -> Any:
    existing_model_name = crud.model.get_by_user_and_name(
        db, user_id=current_user.id, name=model_import.name
    )
    if existing_model_name:
        raise DuplicateModelError()

    if not settings.MODELS_PATH:
        raise InvalidConfiguration()

    model_info = jsonable_encoder(model_import)

    task = create_task_as_placeholder(db, user_id=current_user.id)
    logger.info("[import model] task created and hided: %s", task)

    existing_model_hash = crud.model.get_by_hash(db, hash_=model_import.hash)

    # bind imported model to the placeholding task
    model_info["task_id"] = task.id
    model_info["user_id"] = current_user.id
    model_in = schemas.ModelCreate(**model_info)
    model = crud.model.create(db, obj_in=model_in)
    logger.info("[import model] model record created: %s", model)

    if existing_model_hash:
        logger.info(
            "model of same hash (%s) exists, just add a new reference",
            model_import.hash,
        )
    else:
        background_tasks.add_task(
            save_model_file, model_import.input_url, settings.MODELS_PATH
        )


def create_task_as_placeholder(db: Session, *, user_id: int) -> Task:
    task_id = ControllerRequest.gen_task_id(user_id)
    task_in = schemas.TaskCreate(name=task_id, type=TaskType.import_data)
    task = crud.task.create_task(db, obj_in=task_in, task_hash=task_id, user_id=user_id)
    crud.task.soft_remove(db, id=task.id)
    return task


def save_model_file(model_url: str, storage_path: str) -> None:
    logger.info("[import model] start importing model file from %s", model_url)
    save_file(model_url, storage_path)


@router.delete(
    "/{model_id}",
    response_model=schemas.ModelOut,
    dependencies=[Depends(deps.get_current_active_user)],
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
    stats_client: RedisStats = Depends(deps.get_stats_client),
) -> Any:
    """
    Delete model
    (soft delete actually)
    """
    model = crud.model.get_with_task(db, user_id=current_user.id, id=model_id)
    if not model:
        raise ModelNotFound()
    model_keywords = schemas.Model.from_orm(model).keywords

    model = crud.model.soft_remove(db, id=model_id)

    stats_client.delete_model_rank(current_user.id, model_id)
    logger.info("deleted model(%s) from ref count", model_id)
    if model_keywords:
        stats_client.delete_keyword_wise_model_rank(
            current_user.id, model_id, model_keywords
        )
    logger.info("deleted model(%s) from keyword mAP", model_id)
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
    model = crud.model.get_with_task(db, user_id=current_user.id, id=model_id)
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
    model = crud.model.get_by_user_and_name(
        db, user_id=current_user.id, name=model_in.name
    )
    if model:
        raise DuplicateModelError()

    model = crud.model.get(db, id=model_id)
    if not model:
        raise ModelNotFound()
    model = crud.model.update(db, db_obj=model, obj_in=model_in)
    return {"result": model}
