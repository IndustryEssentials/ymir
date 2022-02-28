from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.DatasetGroupPaginationOut)
def list_model_groups(
    db: Session = Depends(deps.get_db),
    name: str = Query(None),
    project_id: int = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
    is_desc: bool = Query(True),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    pass
