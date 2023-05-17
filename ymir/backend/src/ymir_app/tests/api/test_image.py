from typing import Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.api_v1.endpoints import images as m
from app.api.errors.errors import error_codes
from app.config import settings
from app.constants.state import DockerImageType
from tests.utils.utils import random_lower_string
from app.libs import tasks


class TestListImages:
    def test_list_images_success(self, client: TestClient, admin_token_headers):
        r = client.get(
            f"{settings.API_V1_STR}/images/",
            headers=admin_token_headers,
        )
        assert r.ok
        result = r.json()["result"]
        assert result["total"] == len(result["items"])
        assert "is_shared" in result["items"][0]


class TestUpdateImage:
    def test_update_image_name_success(self, client: TestClient, admin_token_headers):
        new_name = random_lower_string()
        r = client.patch(
            f"{settings.API_V1_STR}/images/1",
            headers=admin_token_headers,
            json={"name": new_name},
        )
        assert r.ok
        result = r.json()["result"]
        assert result["name"] == new_name

    def test_update_image_failed_due_to_no_permission(self, client: TestClient, normal_user_token_headers):
        new_name = random_lower_string()
        r = client.patch(
            f"{settings.API_V1_STR}/images/1",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.json()["code"] == error_codes.INVALID_SCOPE


class TestGetImage:
    def test_get_a_single_image_success(self, client: TestClient, admin_token_headers):
        r = client.get(
            f"{settings.API_V1_STR}/images/1",
            headers=admin_token_headers,
        )
        assert r.ok
        result = r.json()["result"]
        assert not result["is_shared"]


class TestCreateImage:
    def test_create_image_success(self, db: Session, client: TestClient, user_id, admin_token_headers, mocker):
        j = {"url": random_lower_string(), "name": random_lower_string()}
        mocker.patch.object(tasks, "ControllerClient", return_value=mocker.Mock())
        r = client.post(f"{settings.API_V1_STR}/images/", headers=admin_token_headers, json=j)
        assert "result_docker_image" in r.json()['result']
        assert r.ok


class TestDeleteImage:
    def test_delete_a_image_success(self, db: Session, client: TestClient, user_id, admin_token_headers, mocker):
        j = {"url": random_lower_string(), "name": random_lower_string()}
        mocker.patch.object(tasks, "ControllerClient", return_value=mocker.Mock())
        r = client.post(f"{settings.API_V1_STR}/images/", headers=admin_token_headers, json=j)
        i = r.json()['result']['result_docker_image']['id']
        r = client.delete(
            f"{settings.API_V1_STR}/images/{i}",
            headers=admin_token_headers,
        )
        assert r.ok
        assert r.json()["result"]["is_deleted"] == 1


class TestCreateRelationship:
    def test_create_image_relationship_success(self, client: TestClient, admin_token_headers):
        src_image_id = 1
        dest_image_ids = [2, 3]
        r = client.put(
            f"{settings.API_V1_STR}/images/{src_image_id}/related",
            headers=admin_token_headers,
            json={"dest_image_ids": dest_image_ids},
        )
        assert r.ok
        result = r.json()["result"]
        for relationship, dest_image_id in zip(result, dest_image_ids):
            assert relationship["src_image_id"] == src_image_id
            assert relationship["dest_image_id"] == dest_image_id


class TestGetRelationship:
    def test_get_image_relationship_success(self, client: TestClient, admin_token_headers):
        src_image_id = 1
        dest_image_ids = [3]
        r = client.put(
            f"{settings.API_V1_STR}/images/{src_image_id}/related",
            headers=admin_token_headers,
            json={"dest_image_ids": dest_image_ids},
        )
        assert r.ok, "Failed to create relationship beforehand"

        r = client.get(
            f"{settings.API_V1_STR}/images/{src_image_id}/related",
            headers=admin_token_headers,
        )
        assert r.ok
        result = r.json()["result"]
        for relationship, dest_image_id in zip(result, dest_image_ids):
            assert relationship["src_image_id"] == src_image_id
            assert relationship["dest_image_id"] == dest_image_id


def test_parse(mocker: Any) -> None:
    config = {
        DockerImageType.mining: {"A": 1},
        DockerImageType.infer: {"B": 2},
    }
    res = list(m.parse_docker_image_config(config))
    assert len(res) == 2
