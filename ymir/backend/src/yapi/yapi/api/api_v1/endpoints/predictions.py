from typing import Any

from fastapi import APIRouter, Depends, Query, Path
from fastapi.logger import logger

from yapi import schemas
from yapi.api import deps
from yapi.config import settings
from yapi.utils.ymir_app import AppClient
from yapi.utils.data import dump_to_json, exclude_nones

router = APIRouter()


@router.get("/", response_model=schemas.prediction.PredictionPaginationOut)
def list_predictions(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/predictions"
    params = {"project_id": project_id, **dump_to_json(pagination)}
    resp = app.get(url, params=params)
    predictions = resp.json()
    return predictions


@router.get("/{prediction_id}", response_model=schemas.prediction.PredictionOut)
def get_prediction(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    prediction_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/predictions/{prediction_id}"
    resp = app.get(url)
    prediction = resp.json()
    return prediction


@router.get(
    "/{prediction_id}/assets",
    response_model=schemas.prediction.PredictionAssetPaginationOut,
)
def list_prediction_assets(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    prediction_id: int = Path(...),
    pagination: schemas.common.CommonPaginationParams = Depends(),
    class_names: str = Query(None),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/assets/"
    params = {
        "project_id": project_id,
        "data_id": prediction_id,
        "data_type": 2,
        "keywords": class_names,
        **dump_to_json(pagination),
    }
    resp = app.get(url, params=params)
    assets = resp.json()
    return assets


@router.get(
    "/{prediction_id}/evaluation",
    response_model=schemas.prediction.PredictionEvaluationOut,
)
def get_prediction_evaluation(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    prediction_id: int = Path(...),
    project_id: int = Query(...),
    confidence_threshold: float = Query(0.5),
    iou_threshold: float = Query(0.5),
    require_average_iou: bool = Query(False),
    need_pr_curve: bool = Query(False),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/predictions/evaluation"
    payload = {
        "project_id": project_id,
        "prediction_ids": [prediction_id],
        "confidence_threshold": confidence_threshold,
        "iou_threshold": iou_threshold,
        "require_average_iou": require_average_iou,
        "need_pr_curve": need_pr_curve,
    }
    resp = app.post(url, json=exclude_nones(payload))
    evaluation_result = resp.json()
    logger.info("url: %s, payload: %s, resp: %s", url, payload, evaluation_result)
    return evaluation_result
