from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.config import settings

router = APIRouter()


@router.get("/", response_model=schemas.RoleOut)
def list_roles(
    db: Session = Depends(deps.get_db),
    offset: int = 0,
    limit: int = settings.DEFAULT_LIMIT,
) -> Any:
    """
    List all the roles for User
    """
    roles = crud.role.get_multi(db, offset=offset, limit=limit)
    return roles
