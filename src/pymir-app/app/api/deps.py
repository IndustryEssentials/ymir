from typing import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.errors.errors import (
    InactiveUser,
    InvalidToken,
    UserNotAdmin,
    UserNotFound,
    WorkspaceNotFound,
)
from app.config import settings
from app.db.session import SessionLocal
from app.utils import graph, security, stats, ymir_controller, ymir_viz

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


# Dependents
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise InvalidToken()
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise UserNotFound()
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if crud.user.is_deleted(current_user):
        raise InactiveUser()
    return current_user


def get_current_workspace(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> models.Workspace:
    workspace = crud.workspace.get_by_user_id(db, user_id=current_user.id)
    if not workspace:
        raise WorkspaceNotFound()
    return workspace


def get_current_active_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_admin(current_user):
        raise UserNotAdmin()
    return current_user


def get_controller_client() -> Generator:
    try:
        client = ymir_controller.ControllerClient(settings.GRPC_CHANNEL)
        yield client
    finally:
        client.close()


def get_viz_client() -> Generator:
    try:
        client = ymir_viz.VizClient(
            host=settings.VIZ_HOST,
        )
        yield client
    finally:
        client.close()


def get_graph_client(
    current_user: models.User = Depends(get_current_active_user),
) -> Generator:
    try:
        client = graph.GraphClient(redis_uri=settings.REDIS_URI)
        client.user_id = current_user.id
        yield client
    finally:
        client.close()


def get_stats_client(
    current_user: models.User = Depends(get_current_active_user),
) -> Generator:
    task_types = [t.value for t in models.task.TaskType]
    try:
        client = stats.RedisStats(settings.REDIS_URI, task_types)
        yield client
    finally:
        client.close()
