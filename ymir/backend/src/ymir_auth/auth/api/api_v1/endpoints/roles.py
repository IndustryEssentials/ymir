from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import crud, schemas
from auth.api import deps
from auth.config import settings

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
