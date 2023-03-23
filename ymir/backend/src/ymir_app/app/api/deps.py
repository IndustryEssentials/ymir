from typing import Generator

from fastapi import Depends, Security, Header
from fastapi.logger import logger
from fastapi.security import APIKeyHeader

from app import schemas
from app.api.errors.errors import (
    InvalidScope,
    InvalidToken,
    UserNotFound,
)
from app.config import settings
from app.constants.role import Roles
from app.db.session import SessionLocal
from app.utils import cache as ymir_cache
from app.utils import ymir_controller, ymir_viz
from app.utils.security import verify_api_key
from app.utils.ymir_controller import ControllerClient
from common_utils.labels import UserLabels


API_KEY_NAME = "api-key"  # use dash to compatible with Nginx
api_key_header = APIKeyHeader(name=API_KEY_NAME, scheme_name="API key header", auto_error=False)


# Dependents

# apiKey approach
def api_key_security(header_param: str = Security(api_key_header)) -> str:
    if header_param and verify_api_key(header_param):
        return header_param
    else:
        raise InvalidToken()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


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


def get_controller_client() -> Generator:
    try:
        client = ymir_controller.ControllerClient(settings.GRPC_CHANNEL)
        yield client
    finally:
        client.close()


def get_viz_client() -> Generator:
    try:
        client = ymir_viz.VizClient()
        yield client
    finally:
        client.close()


def get_cache(
    current_user: schemas.user.UserInfo = Depends(get_current_active_user),
) -> Generator:
    try:
        cache_client = ymir_cache.CacheClient(redis_uri=settings.BACKEND_REDIS_URL, user_id=current_user.id)
        yield cache_client
    finally:
        cache_client.close()


def get_user_labels(
    current_user: schemas.user.UserInfo = Depends(get_current_active_user),
    cache: ymir_cache.CacheClient = Depends(get_cache),
    controller_client: ControllerClient = Depends(get_controller_client),
) -> UserLabels:
    # todo: make a cache wrapper
    cached = cache.get(ymir_cache.KEYWORDS_CACHE_KEY)
    if cached:
        logger.info("cache hit")
        return UserLabels.parse_raw(cached)

    logger.info("cache miss")
    user_labels = controller_client.get_labels_of_user(current_user.id)

    cache.set(ymir_cache.KEYWORDS_CACHE_KEY, user_labels.json())
    return user_labels
