from typing import Any

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import MessageNotFound

router = APIRouter()


@router.get("/", response_model=schemas.message.MessagePaginationOut)
def list_messages(
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    project_id: int = Query(None),
    pagination: schemas.CommonPaginationParams = Depends(),
) -> Any:
    messages, total = crud.message.get_multi_messages(
        db,
        user_id=current_user.id,
        project_id=project_id,
        pagination=pagination,
    )
    return {"result": {"total": total, "items": messages}}


@router.get("/{message_id}", response_model=schemas.message.MessageOut)
def get_message(
    *,
    db: Session = Depends(deps.get_db),
    message_id: int = Path(...),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a message detail
    """
    message = crud.message.get(db, id=message_id)
    if not message:
        raise MessageNotFound()
    return {"result": message}


@router.patch("/{message_id}", response_model=schemas.message.MessageOut)
def update_message(
    *,
    db: Session = Depends(deps.get_db),
    message_id: int = Path(...),
    message_update: schemas.message.MessageUpdate,
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change message is_read state
    """
    message = crud.message.get_by_user_and_id(db, user_id=current_user.id, id=message_id)
    if not message:
        raise MessageNotFound()

    message = crud.message.update(db, db_obj=message, obj_in=message_update)
    return {"result": message}
