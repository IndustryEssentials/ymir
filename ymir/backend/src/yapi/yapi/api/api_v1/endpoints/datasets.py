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


@router.get("/", response_model=schemas.dataset.DatasetPaginationOut)
def list_datasets(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    name: str = Query(None, description="search by dataset name"),
    pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/dataset_groups"
    params = {"name": name, "project_id": project_id, **dump_to_json(pagination)}
    logger.info("url: %s, params: %s", url, params)
    resp = app.get(url, params=params)
    datasets = resp.json()
    return datasets


@router.get("/{dataset_id}", response_model=schemas.dataset.DatasetOut)
def get_dataset(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    dataset_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/dataset_groups/{dataset_id}"
    logger.info("url: %s, params: %s", url, None)
    resp = app.get(url)
    datasets = resp.json()
    return datasets


@router.get(
    "/{dataset_id}/versions", response_model=schemas.dataset.DatasetVersionPaginationOut
)
def list_dataset_versions(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    dataset_id: int = Path(...),
    state: ResultState = Query(None),
    pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/datasets/"
    params = {
        "project_id": project_id,
        "group_id": dataset_id,
        **dump_to_json(pagination),
    }
    if state:
        params["state"] = state.value
    # TODO
    #  helper to convert any object to valid json dict for forwarding to APP
    resp = app.get(url, params=params)
    dataset_versions = resp.json()
    logger.info("url: %s, params: %s, resp: %s", url, params, dataset_versions)
    return dataset_versions


@router.get(
    "/{dataset_id}/versions/{dataset_version_id}",
    response_model=schemas.dataset.DatasetVersionOut,
)
def get_dataset_version(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    dataset_id: int = Path(...),
    dataset_version_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/datasets/{dataset_version_id}"
    logger.info("url: %s, params: %s", url, None)
    resp = app.get(url, params={"verbose": True})
    dataset = resp.json()
    return dataset


@router.get(
    "/{dataset_id}/versions/{dataset_version_id}/assets",
    response_model=schemas.dataset.DatasetAssetPaginationOut,
)
def list_dataset_assets(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Query(...),
    dataset_id: int = Path(...),
    dataset_version_id: int = Path(...),
    pagination: schemas.common.CommonPaginationParams = Depends(),
    class_names: str = Query(None),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/assets/"
    params = {
        "project_id": project_id,
        "data_id": dataset_version_id,
        "data_type": 1,
        "keywords": class_names,
        **dump_to_json(pagination),
    }
    logger.info("url: %s, params: %s", url, params)
    resp = app.get(url, params=params)
    assets = resp.json()
    return assets
