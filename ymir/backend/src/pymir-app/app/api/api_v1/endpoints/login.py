from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import (
    InactiveUser,
    IncorrectEmailOrPassword,
    InvalidToken,
    UserNotFound,
)
from app.config import settings
from app.utils import security
from app.utils.email import send_reset_password_email

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
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise IncorrectEmailOrPassword()
    elif crud.user.is_deleted(user):
        raise InactiveUser()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
    return {"result": payload, **payload}


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Recover password
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise UserNotFound()
    password_reset_token = security.generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
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
