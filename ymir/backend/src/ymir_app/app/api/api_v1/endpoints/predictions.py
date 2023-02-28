from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.constants.state import ObjectType, ResultState, TaskType

router = APIRouter()


@router.get("/", response_model=schemas.prediction.PredictionsOut)
def list_predictions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    project_id: int = Query(None),
    source: TaskType = Query(None, description="type of related task"),
    visible: bool = Query(True),
    state: ResultState = Query(None),
    object_type: ObjectType = Query(None),
    pagination: schemas.CommonPaginationParams = Depends(),
) -> Any:
    crud.prediction.get_multi_with_filters(db, user_id=current_user.id, project_id=project_id, pagination=pagination)
