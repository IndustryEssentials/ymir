from typing import Generator

import pytest
from fastapi.testclient import TestClient

from monitor.libs.redis_handler import init_redis_pool
from monitor.main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def clear_redislite():
    redis_client = init_redis_pool()
    redis_client.flushall()
