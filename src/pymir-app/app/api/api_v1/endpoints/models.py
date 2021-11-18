import random
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import DuplicateModelError, ModelNotFound, NoModelPermission
from app.models.task import TaskType
from app.utils.stats import RedisStats

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.ModelOut,
    dependencies=[Depends(deps.get_current_active_user)],
)
def list_models(
    db: Session = Depends(deps.get_db),
    model_ids: str = Query(None, example="12,13,14", alias="ids"),
    name: str = Query(None, description="search by model's name"),
    source: TaskType = Query(None, description="the type of related task", example=1),
    offset: int = Query(None),
    limit: int = Query(None),
    sort_by_map: bool = Query(None, description="sort model by mAP"),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of models,
    pagination is supported by means of offset and limit
    """
    ids = [int(i) for i in model_ids.split(",")] if model_ids else []
    models, total = crud.model.get_multi_models(
        db,
        user_id=current_user.id,
        ids=ids,
        name=name,
        task_type=source,
        offset=offset,
        limit=limit,
        order_by="map" if sort_by_map else None,
        start_time=start_time,
        end_time=end_time,
    )
    payload = {"total": total, "items": models}
    return {"result": payload}


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
    model = crud.model.get(db, id=model_id)
    if not model:
        raise ModelNotFound()

    if model.user_id != current_user.id:
        raise NoModelPermission()

    model = crud.model.soft_remove(db, id=model_id)
    stats_client.delete_model_rank(current_user.id, model_id)
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
