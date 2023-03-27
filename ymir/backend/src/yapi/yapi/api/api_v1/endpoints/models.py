from typing import Any

from fastapi import APIRouter, Depends, Query, Path
from fastapi.logger import logger

from yapi import schemas
from yapi.api import deps
from yapi.config import settings
from yapi.constants.state import ResultState
from yapi.utils.ymir_app import AppClient
from yapi.utils.data import dump_to_json

router = APIRouter()


@router.get("/", response_model=schemas.model.ModelPaginationOut)
def list_models(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    name: str = Query(None, description="search by model name"),
    pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/model_groups"
    params = {"name": name, "project_id": project_id, **dump_to_json(pagination)}
    logger.info("url: %s, params: %s", url, params)
    resp = app.get(url, params=params)
    datasets = resp.json()
    return datasets


@router.get("/{model_id}", response_model=schemas.model.ModelOut)
def get_model(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    model_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/model_groups/{model_id}"
    resp = app.get(url)
    models = resp.json()
    return models


@router.get(
    "/{model_id}/versions", response_model=schemas.model.ModelVersionPaginationOut
)
def list_model_versions(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    model_id: int = Path(...),
    state: ResultState = Query(None),
    pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/models/"
    params = {
        "group_id": model_id,
        **dump_to_json(pagination),
    }
    if state:
        params["state"] = state.value
    # TODO
    #  helper to convert any object to valid json dict for forwarding to APP
    resp = app.get(url, params=params)
    model_versions = resp.json()
    return model_versions


@router.get(
    "/{model_id}/versions/{model_version_id}",
    response_model=schemas.model.ModelVersionOut,
)
def get_model_version(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    model_id: int = Path(...),
    model_version_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/models/{model_version_id}"
    resp = app.get(url, params={"verbose": True})
    model = resp.json()
    return model
