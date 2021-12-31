from fastapi.testclient import TestClient

from app.api.errors import error_codes
from app.config import settings
from tests.utils.utils import random_lower_string


class TestListImages:
    def test_list_images_success(self, client: TestClient, admin_token_headers):
        r = client.get(
            f"{settings.API_V1_STR}/images/",
            headers=admin_token_headers,
        )
        assert r.ok
        result = r.json()["result"]
        assert result["total"] == len(result["items"])


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

    def test_update_image_failed_due_to_no_permission(
        self, client: TestClient, normal_user_token_headers
    ):
        new_name = random_lower_string()
        r = client.patch(
            f"{settings.API_V1_STR}/images/1",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.json()["code"] == error_codes.INVALID_SCOPE


class TestCreateRelationship:
    def test_create_image_relationship_success(
        self, client: TestClient, admin_token_headers
    ):
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
    def test_get_image_relationship_success(
        self, client: TestClient, admin_token_headers
    ):
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
