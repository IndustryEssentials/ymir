import json
from typing import Dict, Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from auth.config import settings
from auth.db.session import SessionLocal
from auth.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_admin_token_headers, get_super_admin_token_headers


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


def fake_cache_client() -> Generator:
    try:
        client = Mock()
        user_labels = {
            "labels": [
                {
                    "name": "tabby",
                    "aliases": [],
                    "create_time": 1647075211.0,
                    "update_time": 1647075210.0,
                    "id": 0,
                },
                {
                    "id": 1,
                    "name": "kitten",
                    "aliases": [],
                    "create_time": 1647076209.0,
                    "update_time": 1647076408.0,
                },
            ]
        }
        client.get.return_value = json.dumps(user_labels)
        yield client
    finally:
        client.close()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def api_key_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return {"api-key": settings.APP_API_KEY}


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(client=client, email=settings.EMAIL_TEST_USER, db=db)


@pytest.fixture(scope="module")
def admin_token_headers(client: TestClient) -> Dict[str, str]:
    return get_admin_token_headers(client)


@pytest.fixture(scope="module")
def super_admin_token_headers(client: TestClient) -> Dict[str, str]:
    return get_super_admin_token_headers(client)


@pytest.fixture()
def user_id(mocker, client: TestClient, normal_user_token_headers: Dict[str, str]):
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()["result"]
    return current_user["id"]
