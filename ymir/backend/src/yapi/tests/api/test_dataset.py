from typing import Dict

from fastapi.testclient import TestClient

from yapi.config import settings
from tests.utils.utils import gen_dataset_data, gen_dataset_version_data


class TestListDatasets:
    def test_list_datasets_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_dataset_data(i) for i in range(total)]}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(
            f"{settings.API_V1_STR}/datasets/", params={"project_id": 100}, headers=normal_user_token_headers
        )
        assert len(r.json()["result"]["items"]) == r.json()["result"]["total"] == total


class TestGetDataset:
    def test_get_dataset_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        dataset_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_dataset_data(dataset_id)}
        r = client.get(f"{settings.API_V1_STR}/datasets/{dataset_id}", headers=normal_user_token_headers)
        dataset = r.json()["result"]
        assert dataset["id"] == dataset_id


class TestListDatasetVersions:
    def test_list_dataset_versions_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_dataset_version_data(i) for i in range(total)]}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(
            f"{settings.API_V1_STR}/datasets/1/versions", params={"project_id": 100}, headers=normal_user_token_headers
        )
        assert len(r.json()["result"]["items"]) == total == r.json()["result"]["total"]


class TestGetDatasetVersion:
    def test_get_dataset_version_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        version_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_dataset_version_data(version_id)}
        r = client.get(f"{settings.API_V1_STR}/datasets/1/versions/{version_id}", headers=normal_user_token_headers)
        resp = r.json()["result"]
        assert resp["id"] == version_id
