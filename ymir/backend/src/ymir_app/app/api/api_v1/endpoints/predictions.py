from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.utils.data import groupby
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.prediction.PredictionPaginationOut)
def list_predictions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_id: int = Query(None),
    visible: bool = Query(True),
    pagination: schemas.CommonPaginationParams = Depends(),
) -> Any:
    predictions, total = crud.prediction.get_multi_with_filters(
        db,
        user_id=current_user.id,
        project_id=project_id,
        visible=visible,
        pagination=pagination,
    )
    model_wise_predictions = groupby(predictions, "model_id")
    return {"result": {"total": total, "items": model_wise_predictions}}
