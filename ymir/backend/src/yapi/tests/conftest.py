from typing import Dict, Generator
from unittest.mock import Mock, MagicMock

import pytest
from fastapi.testclient import TestClient

from yapi.api import deps
from yapi.config import settings
from yapi.main import app
from yapi.utils.ymir_app import AppClient
from tests.utils.utils import get_normal_token_headers, get_admin_token_headers, get_super_admin_token_headers


@pytest.fixture(scope="module")
def api_key_headers(client: TestClient) -> Dict[str, str]:
    return {"api-key": settings.APP_API_KEY}


@pytest.fixture(scope="module")
def normal_user_token_headers() -> Dict[str, str]:
    return get_normal_token_headers()


@pytest.fixture(scope="module")
def admin_token_headers() -> Dict[str, str]:
    return get_admin_token_headers()


@pytest.fixture(scope="module")
def super_admin_token_headers() -> Dict[str, str]:
    return get_super_admin_token_headers()


@pytest.fixture()
def user_id(normal_user_token_headers: Dict[str, str]):
    return int(normal_user_token_headers["X-User-Id"])


@pytest.fixture()
def mock_app():
    user_info = Mock(id=233, role=Mock(value=1))
    client = AppClient(user_info=user_info)
    client.get = MagicMock()
    client.post = MagicMock()
    return client


def fake_app_client() -> Generator:
    try:
        client = mock_app()
        yield client
    finally:
        client.close()


@pytest.fixture()
def client(mock_app) -> Generator:
    app.dependency_overrides[deps.get_app_client] = lambda: mock_app
    with TestClient(app) as c:
        yield c
