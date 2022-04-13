from typing import Generator

from fastapi import Depends, Security
from fastapi.logger import logger
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.errors.errors import (
    InactiveUser,
    InvalidScope,
    InvalidToken,
    UserNotFound,
)
from app.config import settings
from app.constants.role import Roles
from app.db.session import SessionLocal
from app.utils import cache as ymir_cache
from app.utils import graph, security, ymir_controller, ymir_viz
from app.utils.clickhouse import YmirClickHouse
from app.utils.security import verify_api_key
from app.utils.ymir_controller import ControllerClient
from common_utils.labels import UserLabels

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    scopes={role.name: role.description for role in [Roles.NORMAL, Roles.ADMIN, Roles.SUPER_ADMIN]},
)

API_KEY_NAME = "api-key"  # use dash to compatible with Nginx
api_key_header = APIKeyHeader(name=API_KEY_NAME, scheme_name="API key header", auto_error=False)


# Dependents

# apiKey approach
def api_key_security(header_param: str = Security(api_key_header)) -> str:
    if header_param and verify_api_key(header_param):
        return header_param
    else:
        raise InvalidToken()


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


def get_controller_client() -> Generator:
    try:
        client = ymir_controller.ControllerClient(settings.GRPC_CHANNEL)
        yield client
    finally:
        client.close()


def get_viz_client() -> Generator:
    try:
        client = ymir_viz.VizClient(host=settings.VIZ_HOST)
        yield client
    finally:
        client.close()


def get_graph_client() -> Generator:
    try:
        client = graph.GraphClient(redis_uri=settings.BACKEND_REDIS_URL)
        yield client
    finally:
        client.close()


def get_graph_client_of_user(
    current_user: models.User = Depends(get_current_active_user),
) -> Generator:
    try:
        client = graph.GraphClient(redis_uri=settings.BACKEND_REDIS_URL)
        client.user_id = current_user.id
        yield client
    finally:
        client.close()


def get_cache(
    current_user: models.User = Depends(get_current_active_user),
) -> Generator:
    try:
        cache_client = ymir_cache.CacheClient(settings.BACKEND_REDIS_URL, current_user.id)
        yield cache_client
    finally:
        cache_client.close()


def get_user_labels(
        current_user: models.User = Depends(get_current_active_user),
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


def get_clickhouse_client() -> Generator:
    try:
        clickhouse_client = YmirClickHouse(settings.CLICKHOUSE_URI)
        yield clickhouse_client
    finally:
        clickhouse_client.close()
