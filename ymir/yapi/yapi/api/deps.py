
from fastapi import Depends, Header

from yapi import schemas
from yapi.api.errors.errors import (
    InvalidScope,
    UserNotFound,
)
from yapi.constants.role import Roles
from yapi.utils.ymir_app import AppClient


def get_user_info_from_x_headers(
    x_user_id: str = Header(default=None),
    x_user_role: str = Header(default=None),
) -> schemas.user.UserInfo:
    if not x_user_id:
        raise UserNotFound()
    return schemas.user.UserInfo(id=x_user_id, role=x_user_role)


def get_current_active_user(
    current_user: schemas.user.UserInfo = Depends(get_user_info_from_x_headers),
) -> schemas.user.UserInfo:
    if current_user.role < Roles.NORMAL.rank:
        raise InvalidScope()
    return current_user


def get_current_active_admin(
    current_user: schemas.user.UserInfo = Depends(get_user_info_from_x_headers),
) -> schemas.user.UserInfo:
    if current_user.role < Roles.ADMIN.rank:
        raise InvalidScope()
    return current_user


def get_current_active_super_admin(
    current_user: schemas.user.UserInfo = Depends(get_user_info_from_x_headers),
) -> schemas.user.UserInfo:
    if current_user.role < Roles.SUPER_ADMIN.rank:
        raise InvalidScope()
    return current_user


def get_app_client(
    current_user: schemas.user.UserInfo = Depends(get_current_active_user),
) -> AppClient:
    client = AppClient(user_info=current_user)
    return client
