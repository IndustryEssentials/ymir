import json
from typing import Dict, Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.db.session import SessionLocal
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_admin_token_headers


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


def fake_controller_client() -> Generator:
    try:
        client = Mock()
        yield client
    finally:
        client.close()


def fake_stats_client() -> Generator:
    try:
        client = Mock()
        client.get_task_stats.return_value = {}
        client.get_top_models.return_value = [(1, 10), (2, 9), (3, 8)]
        client.get_keyword_wise_best_models.return_value = {"cat": [(1, 0.2), (10, 0.3)], "dog": [(2, 1.0), (9, 3.1)]}
        client.get_top_datasets.return_value = [(10, 10), (20, 9), (30, 8)]
        yield client
    finally:
        client.close()


def fake_viz_client() -> Generator:
    try:
        client = Mock()
        asset = {
            "url": "",
            "hash": "",
            "annotations": [],
            "keywords": [],
            "metadata": {},
        }
        assets = Mock(total=1, items=[asset], keywords={})
        client.get_assets.return_value = assets
        client.get_asset.return_value = asset
        yield client
    finally:
        client.close()


def fake_graph_client() -> Generator:
    try:
        client = Mock()
        nodes = [
            {"id": 1, "name": "n1", "hash": "h1", "type": 1},
            {"id": 2, "name": "n2", "hash": "h2", "type": 2},
        ]
        edges = [{"target": "h1", "source": "h2", "task": {"id": 1}}]
        client.query_history.return_value = {"nodes": nodes, "edges": edges}
        yield client
    finally:
        client.close()


def fake_cache_client() -> Generator:
    try:
        client = Mock()
        labels = ["0,cat,pussy", "1,dog,puppy"]
        client.get.return_value = json.dumps(labels)
        yield client
    finally:
        client.close()

app.dependency_overrides[deps.get_controller_client] = fake_controller_client
app.dependency_overrides[deps.get_stats_client] = fake_stats_client
app.dependency_overrides[deps.get_viz_client] = fake_viz_client
app.dependency_overrides[deps.get_graph_client] = fake_graph_client
app.dependency_overrides[deps.get_cache] = fake_cache_client


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="module")
def admin_token_headers(client: TestClient) -> Dict[str, str]:
    return get_admin_token_headers(client)
