from typing import Dict

from fastapi.testclient import TestClient

from yapi.config import settings
from tests.utils.utils import gen_model_data, gen_model_version_data


class TestListModels:
    def test_list_models_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_model_data(i) for i in range(total)]}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(f"{settings.API_V1_STR}/models/", params={"project_id": 100}, headers=normal_user_token_headers)
        assert len(r.json()["result"]["items"]) == r.json()["result"]["total"] == total


class TestGetModel:
    def test_get_model_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        model_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_model_data(model_id)}
        r = client.get(f"{settings.API_V1_STR}/models/233", headers=normal_user_token_headers)
        model = r.json()["result"]
        assert model["id"] == model_id


class TestListModelVersions:
    def atest_list_model_versions_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_model_version_data(i) for i in range(total)]}
        app_resp = {"total": total, "items": []}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(
            f"{settings.API_V1_STR}/models/1/versions", params={"project_id": 100}, headers=normal_user_token_headers
        )
        assert len(r.json()["result"]["items"]) == total == r.json()["result"]["total"]


class TestGetModelVersion:
    def test_get_model_version_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        version_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_model_version_data(version_id)}
        r = client.get(f"{settings.API_V1_STR}/models/1/versions/{version_id}", headers=normal_user_token_headers)
        resp = r.json()["result"]
        assert resp["id"] == version_id
