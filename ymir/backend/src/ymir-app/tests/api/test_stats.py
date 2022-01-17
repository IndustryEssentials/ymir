from typing import Dict

from fastapi.testclient import TestClient

from app.config import settings


class TestGetStats:
    def test_get_stats_for_model(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.get(
            f"{settings.API_V1_STR}/stats/models/hot",
            headers=normal_user_token_headers,
        )
        res = r.json()
        assert res["code"] == 0
        assert res["result"]

    def test_get_stats_for_dataset(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.get(
            f"{settings.API_V1_STR}/stats/datasets/hot",
            headers=normal_user_token_headers,
            params={"q": "dataset"},
        )
        res = r.json()
        assert res["code"] == 0
        assert res["result"]
