from datetime import datetime
from enum import Enum
from typing import Any
import enum
from fastapi import APIRouter, Depends, Query, Path

from app import models, schemas
from app.api import deps
from app.utils.clickhouse import YmirClickHouse

router = APIRouter()


@router.post(
    "/", response_model=schemas.Project,
)
def create_project(project_paras: schemas.ProjectCreateParameter) -> Any:
    pass


@router.get(
    "/", response_model=schemas.ProjectPaginationOut,
)
def get_project(offset: int = Query(None), limit: int = Query(None), is_desc: bool = Query(True),) -> Any:
    pass


@router.put(
    "/{project_id}", response_model=schemas.Project,
)
def update_project(project_id: int, project_paras: schemas.ProjectCreateParameter) -> Any:
    pass


@router.delete(
    "/{project_id}",
    response_model=schemas.Project,
    responses={400: {"description": "No permission"}, 404: {"description": "Task Not Found"},},
)
def delete_project(
    project_id: int = Path(..., example="12"), offset: int = Query(None), limit: int = Query(None),
) -> Any:
    pass
