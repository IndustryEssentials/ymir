from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Path
from fastapi.logger import logger

from yapi import schemas
from yapi.config import settings
from yapi.api import deps
from yapi.utils.ymir_app import AppClient
from yapi.utils.data import dump_to_json


router = APIRouter()


# APIs: get and terminate
@router.get("/", response_model=schemas.task.TaskPaginationOut)
def list_tasks(
        app: AppClient = Depends(deps.get_app_client),
        current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
        name: str = Query(None, description="search by task name"),
        task: str = Query(None, description="search by task type"),
        state: str = Query(None, description="search by task state"),
        pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/tasks"
    params = {"name": name, "type": task, "state": state, **dump_to_json(pagination)}
    logger.info("url: %s, params: %s", url, None)
    resp_json = app.get(url, params=params).json()
    return resp_json


@router.get("/{task_id}", response_model=schemas.task.TaskOut)
def get_task(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/tasks/{task_id}"
    logger.info("url: %s, params: %s", url, None)
    resp_json = app.get(url).json()
    return resp_json


@router.post("/{task_id}/terminate", response_model=schemas.common.Common)
def terminate_task(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_id: int = Path(...),
    fetch_result: bool = Body(..., embed=True),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/tasks/{task_id}/terminate"
    params = {"fetch_result": fetch_result}
    logger.info("url: %s, params: %s", url, params)
    resp_json = app.post(url, json=params).json()
    return resp_json 
