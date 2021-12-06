from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from tests.utils.utils import random_email, random_lower_string


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()["result"]
    assert current_user
    assert current_user["is_deleted"] is False
    assert current_user["is_admin"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user_new_email(
    client: TestClient, admin_token_headers: Dict, db: Session
) -> None:
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/users/", json=data)
    assert 200 <= r.status_code < 300
    created_user = r.json()["result"]
    user = client.get(
        f"{settings.API_V1_STR}/users/{created_user['id']}",
        headers=admin_token_headers,
    )
    assert user
    assert user.json()["result"]["email"] == created_user["email"]
