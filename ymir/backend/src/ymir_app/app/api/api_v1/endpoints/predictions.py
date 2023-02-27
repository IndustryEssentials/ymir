from typing import Optional, Any
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.config import settings
from app.constants.state import ObjectType, ResultState, TaskType
from app.utils.ymir_viz import VizClient
from common_utils.labels import UserLabels

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


@router.get(
    "/{prediction_id}/assets",
    response_model=schemas.AssetPaginationOut,
    responses={404: {"description": "Dataset Not Found"}},
)
def get_assets_of_prediction(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    offset: int = 0,
    limit: int = settings.DEFAULT_LIMIT,
    keywords_str: Optional[str] = Query(None, example="person,cat", alias="keywords"),
    in_cm_types_str: Optional[str] = Query(None, example="tp,mtp", alias="in_cm_types"),
    ex_cm_types_str: Optional[str] = Query(None, example="tp,mtp", alias="ex_cm_types"),
    cks_str: Optional[str] = Query(None, example="shenzhen,shanghai", alias="cks"),
    tags_str: Optional[str] = Query(None, example="big,small", alias="tags"),
    annotation_types_str: Optional[str] = Query(None, example="gt,pred", alias="annotation_types"),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    pass


@router.get("/{prediction_id}/assets/random", response_model=schemas.AssetOut)
def get_random_asset_id_of_prediction(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    pass


@router.get("/{prediction_id}/assets/{asset_hash}", response_model=schemas.AssetOut)
def get_asset_of_prediction(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    asset_hash: str = Path(..., description="in asset hash format"),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get asset from specific prediction
    """
