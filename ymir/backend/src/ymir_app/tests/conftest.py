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
from tests.utils.user import authentication_token_from_email, create_admin_user
from tests.utils.utils import get_admin_token_headers, get_super_admin_token_headers


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


create_admin_user(SessionLocal())


def fake_controller_client() -> Generator:
    try:
        client = Mock()

        client.send.return_value = {
            "label_collection": {
                "labels": [
                    {
                        "name": "tabby",
                        "aliases": [],
                        "create_time": 1647075219.0,
                        "update_time": 1647075218.0,
                        "id": 0,
                    },
                    {
                        "name": "kitten",
                        "aliases": [],
                        "create_time": 1647075217.0,
                        "update_time": 1647075216.0,
                        "id": 0,
                    },
                ]
            }
        }
        client.add_labels.return_value = {
            "label_collection": {
                "labels": [
                    {
                        "name": "tabby",
                        "aliases": [],
                        "create_time": 1647075215.0,
                        "update_time": 1647075214.0,
                        "id": 0,
                    },
                    {
                        "name": "kitten",
                        "aliases": [],
                        "create_time": 1647075213.0,
                        "update_time": 1647075212.0,
                        "id": 0,
                    },
                ]
            }
        }
        client.get_gpu_info.return_value = {"gpu_count": 233}
        client.pull_docker_image.return_value = {
            "hash_id": "hash_abcd",
            "object_type": 1,
            "docker_image_config": {},
        }
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
        assets = dict(total=1, items=[asset], keywords={})
        dataset_analysis = dict(
            keywords={"gt": ["a"], "pred": ["x"]},
            cks_count={},
            cks_count_total={},
            total_assets_mbytes=20,
            total_assets_count=400,
            gt=None,
            pred=None,
            hist={
                "asset_bytes": [],
                "asset_area": [],
                "asset_quality": [],
                "asset_hw_ratio": [],
            },
        )
        metric_records = [{"legend": "0", "user_id": "1", "count": 95}, {"legend": "1", "user_id": "1", "count": 20}]
        client.get_assets.return_value = assets
        client.get_asset.return_value = asset
        client.get_dataset_analysis.return_value = dataset_analysis
        client.query_metrics.return_value = metric_records
        yield client
    finally:
        client.close()


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


app.dependency_overrides[deps.get_controller_client] = fake_controller_client
app.dependency_overrides[deps.get_viz_client] = fake_viz_client
app.dependency_overrides[deps.get_cache] = fake_cache_client


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
