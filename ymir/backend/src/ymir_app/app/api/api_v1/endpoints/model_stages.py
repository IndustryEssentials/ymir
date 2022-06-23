from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import ModelStageNotFound

router = APIRouter()


@router.get(
    "/{stage_id}",
    response_model=schemas.ModelStageOut,
)
def get_model_stage(
    *,
    db: Session = Depends(deps.get_db),
    model_stage_id: int = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a model stage detail
    """
    model_stage = crud.model_stage.get(db, id=model_stage_id)
    if not model_stage:
        raise ModelStageNotFound()
    return {"result": model_stage}


@router.get(
    "/batch",
    response_model=schemas.ModelStagesOut,
)
def batch_get_models(
    db: Session = Depends(deps.get_db),
    model_stage_ids: str = Query(None, alias="ids"),
) -> Any:
    ids = [int(i) for i in model_stage_ids.split(",")]
    stages = crud.model_stage.get_multi_by_ids(db, ids=ids)
    return {"result": stages}
