from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, Query, Security
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateUserNameError,
    UserNotFound,
    FailedToCreateUser,
)
from app.constants.role import Roles
from app.utils.ymir_controller import ControllerClient

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
    current_user: models.User = Security(
        deps.get_current_active_super_admin,
    ),
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
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise DuplicateUserNameError()

    user_in = schemas.UserCreate(password=password, email=email, phone=phone, username=username)
    user = crud.user.create(db, obj_in=user_in)

    try:
        controller_client.create_user(user_id=user.id)
    except ValueError:
        raise FailedToCreateUser()

    return {"result": user}


@router.get("/me", response_model=schemas.UserOut)
def get_current_user(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get verbose information about current user
    """
    return {"result": current_user}


@router.patch(
    "/me",
    response_model=schemas.UserOut,
    responses={404: {"description": "User Not Found"}},
)
def update_myself(
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    username: str = Body(None),
    phone: str = Body(None),
    avatar: str = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user's information
    """
    current_user_info = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_info)
    if password:
        user_in.password = password
    if username:
        user_in.username = username
    if phone is not None:
        user_in.phone = phone
    if avatar is not None:
        user_in.avatar = avatar
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return {"result": user}


@router.get(
    "/{user_id}",
    response_model=schemas.UserOut,
    responses={404: {"description": "User Not Found"}},
)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Roles.ADMIN.name, Roles.SUPER_ADMIN.name],
    ),
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
    current_user: models.User = Security(
        deps.get_current_active_super_admin,
    ),
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
