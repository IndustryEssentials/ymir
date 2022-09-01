from typing import Dict

from fastapi.testclient import TestClient

from app.config import settings


class TestGetStats:
    def test_keywords_recommend(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.get(
            f"{settings.API_V1_STR}/stats/keywords/recommend",
            params={"dataset_ids": "1"},
            headers=normal_user_token_headers,
        )
        res = r.json()
        assert res["code"] == 0
        assert res["result"]

    def test_get_project_count(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.get(
            f"{settings.API_V1_STR}/stats/projects/count",
            headers=normal_user_token_headers,
            params={"precision": "day"},
        )
        res = r.json()
        assert res["code"] == 0
        assert res["result"]
