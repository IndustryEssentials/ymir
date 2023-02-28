import random

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.api_v1.api import assets as m
from app.api.errors.errors import DatasetNotFound
from app.config import settings
from tests.utils.datasets import create_dataset_record


class TestGetAssets:
    def test_get_assets_of_dataset_succeed(
        self,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        db: Session,
        user_id: int,
    ):
        r = create_dataset_record(db, user_id=user_id)
        dataset_id = r.id
        r = client.get(
            f"{settings.API_V1_STR}/assets",
            headers=normal_user_token_headers,
            params={"project_id": r.project_id, "data_id": dataset_id, "data_type": 1},
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0

    def test_get_assets_of_dataset_not_found(self, client: TestClient, normal_user_token_headers, mocker):
        r = client.get(
            f"{settings.API_V1_STR}/assets",
            headers=normal_user_token_headers,
            params={"project_id": 42, "data_id": "23333333", "data_type": 1},
        )
        assert r.status_code == 404


class TestGetAsset:
    def test_get_asset_by_asset_hash_not_found(self, client: TestClient, normal_user_token_headers, mocker):
        r = client.get(
            f"{settings.API_V1_STR}/assets/abc",
            headers=normal_user_token_headers,
            params={"project_id": 42, "data_id": "23333333", "data_type": 1},
        )
        assert r.status_code == 404

    def test_get_asset_by_asset_hash(
        self,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        db: Session,
        user_id: int,
    ):
        r = create_dataset_record(db, user_id=user_id)
        dataset_id = r.id
        r = client.get(
            f"{settings.API_V1_STR}/assets/abc",
            headers=normal_user_token_headers,
            params={"project_id": r.project_id, "data_id": dataset_id, "data_type": 1},
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0


class TestGetRandomAsset:
    def test_get_random_asset_succeed(
        self,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        db: Session,
        user_id: int,
    ):
        mocker.patch.object(m, "get_random_asset_offset", return_value=1)
        r = create_dataset_record(db, user_id=user_id)
        dataset_id = r.id
        r = client.get(
            f"{settings.API_V1_STR}/assets/random",
            headers=normal_user_token_headers,
            params={"project_id": r.project_id, "data_id": dataset_id, "data_type": 1},
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0

    def test_get_random_asset_not_found(self, client: TestClient, normal_user_token_headers, mocker):
        r = client.get(
            f"{settings.API_V1_STR}/assets/random",
            headers=normal_user_token_headers,
            params={"project_id": 42, "data_id": "233333", "data_type": 1},
        )
        assert r.status_code == 404
        assert r.json()["code"] == DatasetNotFound.code


class TestGetRandomOffset:
    def test_get_random_offset(self, mocker):
        limit = random.randint(100, 200)
        assert 0 <= m.get_random_asset_offset(limit) <= limit
