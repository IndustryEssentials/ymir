from typing import Dict

from fastapi.testclient import TestClient

from yapi.config import settings
from tests.utils.utils import gen_project_data


class TestListProjects:
    def test_list_projects_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_project_data(i) for i in range(total)]}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(
            f"{settings.API_V1_STR}/projects/", params={"project_id": 100}, headers=normal_user_token_headers
        )
        assert len(r.json()["result"]["items"]) == r.json()["result"]["total"] == total


class TestGetProject:
    def test_get_project_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        project_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_project_data(project_id)}
        r = client.get(f"{settings.API_V1_STR}/projects/233", headers=normal_user_token_headers)
        project = r.json()["result"]
        assert project["id"] == project_id
