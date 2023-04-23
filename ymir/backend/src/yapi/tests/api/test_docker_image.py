from typing import Dict

from fastapi.testclient import TestClient

from yapi.config import settings
from tests.utils.utils import gen_docker_image_data


class TestListDockerImages:
    def test_list_docker_images_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_docker_image_data(i) for i in range(total)]}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(
            f"{settings.API_V1_STR}/docker_images/", params={"project_id": 100}, headers=normal_user_token_headers
        )
        assert len(r.json()["result"]["items"]) == r.json()["result"]["total"] == total


class TestGetDockerImage:
    def test_get_docker_image_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        docker_image_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_docker_image_data(docker_image_id)}
        r = client.get(f"{settings.API_V1_STR}/docker_images/233", headers=normal_user_token_headers)
        docker_image = r.json()["result"]
        assert docker_image["id"] == docker_image_id
