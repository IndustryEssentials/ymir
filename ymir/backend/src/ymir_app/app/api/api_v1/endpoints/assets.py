import random
from typing import Any, List, Optional, Union

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import AssetNotFound, DatasetNotFound
from app.config import settings
from app.constants.state import AnnotationType
from app.utils.ymir_viz import VizClient
from common_utils.labels import UserLabels

router = APIRouter()


@router.get("/", response_model=schemas.AssetPaginationOut)
def list_assets(
    project_id: int,
    data_id: int,
    data_type: AnnotationType,
    db: Session = Depends(deps.get_db),
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
    """
    Get asset list of specific dataset,
    pagination is supported by means of offset and limit
    """
    mir_dataset = get_mir_dataset(db, current_user.id, data_id, data_type)
    if not mir_dataset:
        raise DatasetNotFound()

    keywords = keywords_str.split(",") if keywords_str else None
    keyword_ids = user_labels.id_for_names(names=keywords, raise_if_unknown=True)[0] if keywords else None

    viz_client.initialize(user_id=current_user.id, project_id=project_id, user_labels=user_labels)
    assets = viz_client.get_assets(
        dataset_hash=mir_dataset.hash,
        keyword_ids=keyword_ids,
        in_cm_types=stringtolist(in_cm_types_str),
        ex_cm_types=stringtolist(ex_cm_types_str),
        cks=stringtolist(cks_str),
        tags=stringtolist(tags_str),
        annotation_types=stringtolist(annotation_types_str),
        limit=limit,
        offset=offset,
    )
    return {"result": assets}


@router.get("/random", response_model=schemas.AssetOut)
def get_random_asset_id_of_dataset(
    project_id: int,
    data_id: int,
    data_type: AnnotationType,
    db: Session = Depends(deps.get_db),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get random asset from specific dataset
    """
    mir_dataset = get_mir_dataset(db, current_user.id, data_id, data_type)
    if not mir_dataset:
        raise DatasetNotFound()

    offset = get_random_asset_offset(mir_dataset.asset_count)
    viz_client.initialize(
        user_id=current_user.id,
        project_id=project_id,
        user_labels=user_labels,
    )
    assets = viz_client.get_assets(
        dataset_hash=mir_dataset.hash,
        keyword_id=None,
        offset=offset,
        limit=1,
    )
    if assets["total"] == 0:
        raise AssetNotFound()
    return {"result": assets["items"][0]}


def get_random_asset_offset(asset_count: Optional[int]) -> int:
    if not asset_count:
        raise AssetNotFound()
    offset = random.randint(0, asset_count - 1)
    return offset


@router.get("/{asset_hash}", response_model=schemas.AssetOut)
def get_asset_info(
    project_id: int,
    data_id: int,
    data_type: AnnotationType,
    asset_hash: str = Path(..., description="in asset hash format"),
    db: Session = Depends(deps.get_db),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get asset from specific dataset
    """
    mir_dataset = get_mir_dataset(db, current_user.id, data_id, data_type)
    if not mir_dataset:
        raise DatasetNotFound()

    viz_client.initialize(
        user_id=current_user.id,
        project_id=project_id,
        user_labels=user_labels,
    )
    assets = viz_client.get_assets(dataset_hash=mir_dataset.hash, asset_hash=asset_hash, limit=1)
    if assets["total"] == 0:
        raise AssetNotFound()
    return {"result": assets["items"][0]}


def stringtolist(s: Optional[str]) -> Optional[List]:
    if s is None:
        return s
    return s.split(",")


def get_mir_dataset(
    db: Session, user_id: int, data_id: int, data_type: AnnotationType
) -> Optional[Union[models.Dataset, models.Prediction]]:
    crud_caller = crud.dataset if data_type == AnnotationType.gt else crud.prediction
    mir_dataset = crud_caller.get_by_user_and_id(db, user_id=user_id, id=data_id)  # type: ignore
    if not mir_dataset:
        return None
    return mir_dataset
