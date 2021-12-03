from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import DuplicateWorkspaceError, FailedtoCreateWorkspace

router = APIRouter()


@router.get("/", response_model=schemas.RuntimeOut)
def list_runtimes(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    name: str = Query(None),
    hash_: str = Query(None, alias="hash"),
    type_: schemas.runtime.RuntimeType = Query(None, alias="type"),
) -> Any:
    """
    Get docker images and configuration templates

    runtime_type:
    1. training
    2. mining
    """
    runtimes = crud.runtime.get_multi_runtimes(
        db,
        name=name,
        type_=type_,
        hash_=hash_,
    )
    return {"result": runtimes}
