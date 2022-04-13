from typing import Dict

from fastapi.testclient import TestClient

from app.config import settings


class TestGetKeywords:
    def test_get_keyword(self, client: TestClient, normal_user_token_headers: Dict[str, str], mocker):
        r = client.get(
            f"{settings.API_V1_STR}/keywords/",
            headers=normal_user_token_headers,
        )
        res = r.json()
        assert res["result"]["total"] == len(res["result"]["items"])


class TestCreateKeyword:
    def test_create_keyword(self, client: TestClient, normal_user_token_headers: Dict[str, str], mocker):
        j = {
            "keywords": [
                {"name": "water", "aliases": ["shui"]},
                {"name": "girl", "aliases": ["woman"]},
            ],
            "dry_run": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/keywords/",
            headers=normal_user_token_headers,
            json=j,
        )
        res = r.json()
        assert sorted(res["result"]["failed"]) == ['kitten', 'tabby']


class TestUpdateKeyword:
    def test_update_keyword(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.patch(
            f"{settings.API_V1_STR}/keywords/cat",
            headers=normal_user_token_headers,
            json={"aliases": ["kitten", "tabby"]},
        )
        res = r.json()
        assert sorted(res["result"]["failed"]) == ["kitten", "tabby"]
