from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, Query
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateUserNameError,
    DuplicatePhoneError,
    UserNotFound,
    FailedToCreateUser,
)
from app.utils.ymir_controller import ControllerClient, gen_user_hash

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.UsersOut,
)
def list_users(
    db: Session = Depends(deps.get_db),
    offset: int = Query(None),
    limit: int = Query(None),
    state: Optional[schemas.UserState] = Query(None),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_super_admin),
) -> Any:
    """
    Get list of users,
    pagination is supported by means of offset and limit

    UserState:
    - registered = 1
    - active = 2
    - declined = 3
    - deactivated = 4
    """
    users, total = crud.user.get_multi_with_filter(db, offset=offset, limit=limit, state=state)
    return {"result": {"total": total, "items": users}}


@router.post(
    "/",
    response_model=schemas.UserOut,
    responses={400: {"description": "Username Already Exists"}},
)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    password: str = Body(...),
    email: EmailStr = Body(...),
    phone: str = Body(None),
    username: str = Body(None),
) -> Any:
    """
    Register user
    """
    if crud.user.get_by_email(db, email=email):
        raise DuplicateUserNameError()
    if phone and crud.user.get_by_phone(db, phone=phone):
        raise DuplicatePhoneError()

    user_in = schemas.UserCreate(password=password, email=email, phone=phone, username=username)
    user = crud.user.create(db, obj_in=user_in)

    try:
        controller_client.create_user(user_id=user.id)
    except ValueError:
        raise FailedToCreateUser()

    return {"result": user}


@router.get(
    "/{user_id}",
    response_model=schemas.UserOut,
    responses={404: {"description": "User Not Found"}},
)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Query user information,
    Admin permission (Admin and Super admin) is required
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise UserNotFound()

    return {"result": user}


@router.patch(
    "/{user_id}",
    response_model=schemas.UserOut,
    responses={404: {"description": "User Not Found"}},
)
def update_user_state(
    user_id: int,
    state: Optional[schemas.UserState] = Body(None),
    role: Optional[schemas.UserRole] = Body(None),
    is_deleted: Optional[bool] = Body(None),
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_super_admin),
) -> Any:
    """
    Change user state (activate, decline, deactivate, etc),
    Super Admin permission is required
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise UserNotFound()

    if state is not None:
        user = crud.user.update_state(db, user=user, state=state)
    if role is not None:
        user = crud.user.update_role(db, user=user, role=role)
    return {"result": user}


@router.post(
    "/controller",
    response_model=schemas.user.ControllerUserOut,
    dependencies=[Depends(deps.api_key_security)],
)
def create_controller_user(
    *,
    in_user: schemas.user.ControllerUserCreate,
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Register controller user
    """
    try:
        controller_client.create_user(user_id=in_user.user_id)
    except ValueError:
        raise FailedToCreateUser()

    return {"result": {"hash": gen_user_hash(in_user.user_id)}}
