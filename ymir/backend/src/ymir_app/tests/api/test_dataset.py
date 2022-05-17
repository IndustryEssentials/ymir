import random
from typing import Dict

import fastapi
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.api_v1.api import datasets as m
from app.api.errors.errors import DatasetNotFound
from app.config import settings
from tests.utils.dataset_groups import create_dataset_group_record
from tests.utils.datasets import create_dataset_record
from tests.utils.utils import random_lower_string, random_url


@pytest.fixture(scope="function", autouse=True)
def patch_background_task(mocker):
    mocker.patch.object(fastapi, "BackgroundTasks", return_value=mocker.Mock())


@pytest.fixture(scope="function")
def mock_controller(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def mock_db(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def mock_graph_db(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def mock_viz(mocker):
    return mocker.Mock()


class TestListDatasets:
    def test_list_datasets_having_results(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
        db: Session,
        user_id: int,
    ):
        group = create_dataset_group_record(db, user_id)
        for _ in range(3):
            create_dataset_record(db, user_id=user_id, dataset_group_id=group.id)
        r = client.get(
            f"{settings.API_V1_STR}/datasets/", headers=normal_user_token_headers, params={"group_id": group.id}
        )
        datasets = r.json()["result"]["items"]
        total = r.json()["result"]["total"]
        assert len(datasets) == total != 0


class TestBatchGetDatasets:
    def test_list_datasets_not_found(self, client: TestClient, normal_user_token_headers):
        r = client.get(
            f"{settings.API_V1_STR}/datasets/batch",
            headers=normal_user_token_headers,
            params={"ids": "1000,2000,3000"},
        )
        assert r.status_code == 404

    def test_list_datasets_given_ids(
        self,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        db: Session,
        user_id: int,
    ):
        group = create_dataset_group_record(db, user_id=user_id)
        datasets = [create_dataset_record(db, user_id=user_id, dataset_group_id=group.id) for _ in range(3)]
        ids = ",".join([str(d.id) for d in datasets])
        r = client.get(
            f"{settings.API_V1_STR}/datasets/batch",
            headers=normal_user_token_headers,
            params={"ids": ids},
        )
        datasets = r.json()["result"]
        assert len(datasets) == 3


class TestCreateDataset:
    def test_create_dataset_succeed(self, client: TestClient, normal_user_token_headers, mocker):
        mocker.patch.object(m, "import_dataset_in_background")
        j = {
            "group_name": random_lower_string(),
            "version_num": random.randint(100, 200),
            "input_url": random_url(),
            "dataset_group_id": 1,
            "project_id": 1,
            "strategy": 1,
        }
        r = client.post(
            f"{settings.API_V1_STR}/datasets/importing",
            headers=normal_user_token_headers,
            json=j,
        )
        assert r.json()["code"] == 0


class TestDeleteDatasets:
    def test_delete_dataset_succeed(
        self,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        db: Session,
        user_id: int,
    ):
        r = create_dataset_record(db, user_id=user_id)
        dataset_id = r.id
        assert not r.is_deleted

        r = client.delete(
            f"{settings.API_V1_STR}/datasets/{dataset_id}",
            headers=normal_user_token_headers,
        )
        assert r.json()["result"]["is_deleted"]

    def test_delete_dataset_not_found(self, client: TestClient, normal_user_token_headers, mocker):
        r = client.delete(f"{settings.API_V1_STR}/datasets/20000", headers=normal_user_token_headers)
        assert r.status_code == 404


class TestGetDataset:
    def test_get_dataset_succeed(
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
            f"{settings.API_V1_STR}/datasets/{dataset_id}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0
        dataset_res = r.json()["result"]
        assert dataset_res


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
            f"{settings.API_V1_STR}/datasets/{dataset_id}/assets",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0

    def test_get_assets_of_dataset_not_found(self, client: TestClient, normal_user_token_headers, mocker):
        r = client.get(
            f"{settings.API_V1_STR}/datasets/23333333/assets",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404


class TestGetAsset:
    def test_get_asset_by_asset_hash_succeed(self, client: TestClient, normal_user_token_headers, mocker):
        r = client.get(
            f"{settings.API_V1_STR}/datasets/23333333/assets/abc",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404

    def test_get_asset_by_asset_hash_not_found(
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
            f"{settings.API_V1_STR}/datasets/{dataset_id}/assets/abc",
            headers=normal_user_token_headers,
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
            f"{settings.API_V1_STR}/datasets/{dataset_id}/assets/random",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0

    def test_get_random_asset_not_found(self, client: TestClient, normal_user_token_headers, mocker):
        r = client.get(
            f"{settings.API_V1_STR}/datasets/23333/assets/random",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404
        assert r.json()["code"] == DatasetNotFound.code

    def test_get_random_offset(self, mocker):
        limit = random.randint(100, 200)
        dataset = mocker.Mock(asset_count=limit)
        assert 0 <= m.get_random_asset_offset(dataset) <= limit


class TestCreateDataFusion:
    def test_create_dataset_fusion_succeed(
        self,
        client: TestClient,
        normal_user_token_headers,
        db: Session,
        user_id: int,
        mocker,
    ):
        dataset_group_obj = create_dataset_group_record(db, project_id=1, user_id=user_id)
        dataset_obj = create_dataset_record(db, user_id=user_id, dataset_group_id=dataset_group_obj.id)

        j = {
            "project_id": 1,
            "dataset_group_id": dataset_group_obj.id,
            "main_dataset_id": dataset_obj.id,
            "include_datasets": [],
            "include_strategy": 1,
            "exclude_datasets": [],
            "include_labels": [],
            "exclude_labels": [],
        }

        r = client.post(
            f"{settings.API_V1_STR}/datasets/fusion",
            headers=normal_user_token_headers,
            json=j,
        )

        assert r.status_code == 200
        assert r.json()["code"] == 0
