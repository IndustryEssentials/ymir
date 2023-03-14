from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import crud, models, schemas
from auth.api import deps
from auth.api.errors.errors import (
    FailedToSendEmail,
    InactiveUser,
    IncorrectEmailOrPassword,
    InvalidToken,
    NotEligibleRole,
    UserNotFound,
)
from auth.config import settings
from auth.utils import security
from auth.utils.email import send_reset_password_email
from common_utils.version import YMIR_VERSION

router = APIRouter()


@router.post(
    "/auth/token",
    response_model=schemas.TokenOut,
    responses={
        400: {"description": "Incorrect email or password"},
        403: {"description": "Inactive user"},
    },
)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise IncorrectEmailOrPassword()
    if not crud.user.is_active(user):
        raise InactiveUser()
    highest_role = schemas.UserRole(user.role)

    # User can request specific roles
    # choose the role of highest rank yet within limit
    if form_data.scopes:
        claimed_role = max(getattr(schemas.UserRole, scope) for scope in form_data.scopes)
    else:
        claimed_role = highest_role

    # make sure the claimed_role is valid
    if claimed_role > highest_role:
        raise NotEligibleRole()

    # grant user adequate role
    role = min(claimed_role, highest_role)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {
        "id": user.id,
        "role": role.name,
    }
    token_payload["version"] = YMIR_VERSION
    payload = {
        "access_token": security.create_access_token(token_payload, expires_delta=access_token_expires),
        "token_type": "bearer",
    }

    # update last login time
    crud.user.update_login_time(db, user=user)

    return {"result": payload, **payload}


@router.post("/auth/validate", response_model=schemas.Msg)
def validate_token(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Validate JWT
    """
    return {"message": "ok"}


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Recover password
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise UserNotFound()
    password_reset_token = security.generate_password_reset_token(email=email)
    try:
        send_reset_password_email(email_to=user.email, email=email, token=password_reset_token)
    except Exception:
        logger.exception("[reset password] Failed to send email. Please check configuration")
        raise FailedToSendEmail()

    return {"message": "Password recovery email sent"}


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = security.verify_password_reset_token(token)
    if not email:
        raise InvalidToken()
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise UserNotFound()
    elif crud.user.is_deleted(user):
        raise InactiveUser()
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"message": "Password updated successfully"}
