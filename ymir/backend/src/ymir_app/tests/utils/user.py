from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import frontend_hash
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(*, client: TestClient, email: str, password: str) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/auth/token", data=data)
    response = r.json()["result"]
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(username=email, email=email, password=password)
    user = crud.user.create(db=db, obj_in=user_in)
    user = crud.user.activate(db=db, user=user)
    return user


def create_admin_user(db: Session) -> User:
    user_in = UserCreate(
        username="admin", email=settings.FIRST_ADMIN, password=frontend_hash(settings.FIRST_ADMIN_PASSWORD)
    )
    user = crud.user.create(db=db, obj_in=user_in)
    user = crud.user.activate(db=db, user=user)
    user = crud.user.update_role(db, user=user, role=schemas.UserRole.SUPER_ADMIN)
    return user


def authentication_token_from_email(*, client: TestClient, email: str, db: Session) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(username=email, email=email, password=password)
        user = crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(email=email, password=password)
        user = crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user = crud.user.activate(db, user=user)
    return user_authentication_headers(client=client, email=email, password=password)
