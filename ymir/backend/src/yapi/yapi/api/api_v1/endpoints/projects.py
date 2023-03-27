from typing import Any

from fastapi import APIRouter, Depends, Query, Path
from fastapi.logger import logger

from yapi import schemas
from yapi.api import deps
from yapi.config import settings
from yapi.utils.ymir_app import AppClient
from yapi.utils.data import dump_to_json

router = APIRouter()


@router.get("/", response_model=schemas.project.ProjectPaginationOut)
def list_projects(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    name: str = Query(None, description="search by project name"),
    object_type: int = Query(None),
    pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/projects"
    params = {"name": name, "object_type": object_type, **dump_to_json(pagination)}
    resp = app.get(url, params=params)
    projects = resp.json()
    return projects


@router.get("/{project_id}", response_model=schemas.project.ProjectOut)
def get_project(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/projects/{project_id}"
    logger.info("url: %s, params: %s", url, None)
    resp = app.get(url)
    projects = resp.json()
    return projects


@router.post("/", response_model=schemas.project.ProjectOut)
def create_project(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_in: schemas.project.ProjectCreate,
) -> Any:
    """
    Create project
    """
    url = f"{settings.APP_URL_PREFIX}/projects/"
    app_project_in = schemas.project.AppProjectCreate(**project_in.dict())
    resp = app.post(url, json=dump_to_json(app_project_in))
    project = resp.json()
    logger.info("url: %s, params: %s, resp: %s", url, None, project)
    return project
