from typing import Generator

from fastapi import Depends, Security
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from auth import crud, models, schemas
from auth.api.errors.errors import (
    InactiveUser,
    InvalidScope,
    InvalidToken,
    UserNotFound,
    SystemVersionConflict,
)
from auth.config import settings
from auth.constants.role import Roles
from auth.db.session import SessionLocal
from auth.utils import security
from common_utils.version import YMIR_VERSION

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    scopes={role.name: role.description for role in [Roles.NORMAL, Roles.ADMIN, Roles.SUPER_ADMIN]},
)


# Dependents


# OAuth2 approach
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    security_scopes: SecurityScopes,
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> models.User:
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        logger.exception("Invalid JWT token")
        raise InvalidToken()

    if token_data.version != YMIR_VERSION:
        raise SystemVersionConflict()

    user = crud.user.get(db, id=token_data.id)
    if not user:
        raise UserNotFound()

    current_role = min(
        getattr(schemas.UserRole, token_data.role),
        schemas.UserRole(user.role),
    )

    if security_scopes.scopes and current_role.name not in security_scopes.scopes:
        logger.error(
            "Invalid JWT token scope: %s not in %s",
            current_role.name,
            security_scopes.scopes,
        )
        raise InvalidScope()
    return user


def get_current_active_user(
    current_user: models.User = Security(get_current_user, scopes=[]),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise InactiveUser()
    return current_user


def get_current_active_admin(
    current_user: models.User = Security(get_current_user, scopes=[Roles.ADMIN.name, Roles.SUPER_ADMIN.name]),
) -> models.User:
    return current_user


def get_current_active_super_admin(
    current_user: models.User = Security(get_current_user, scopes=[Roles.SUPER_ADMIN.name]),
) -> models.User:
    return current_user
