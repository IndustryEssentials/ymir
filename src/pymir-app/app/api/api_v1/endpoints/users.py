from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.logger import logger
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateUserNameError,
    FailedtoCreateWorkspace,
    UserNotFound,
)
from app.utils.ymir_controller import (
    ControllerClient,
    ControllerRequest,
    ExtraRequestType,
)

router = APIRouter()


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

    user_in = schemas.UserCreate(
        password=password, email=email, phone=phone, username=username
    )
    user = crud.user.create(db, obj_in=user_in)

    # fixme better user to workspace mapping
    workspace_id = f"{user.id:0>6}"
    crud.workspace.create(
        db,
        obj_in=schemas.WorkspaceCreate(
            hash=workspace_id, name=workspace_id, user_id=user.id
        ),
    )
    req = ControllerRequest(ExtraRequestType.create_workspace, user.id, workspace_id)
    try:
        resp = controller_client.send(req)
        logger.info("controller response: %s", resp)
    except ValueError:
        # todo parse error message
        raise FailedtoCreateWorkspace()

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
    if phone:
        user_in.phone = phone
    if avatar:
        user_in.avatar = avatar
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return {"result": user}


@router.get(
    "/{user_id}",
    response_model=schemas.UserOut,
    dependencies=[Depends(deps.get_current_active_admin)],
    responses={404: {"description": "User Not Found"}},
)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Query user information,
    Admin permission is required
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise UserNotFound()

    return {"result": user}
