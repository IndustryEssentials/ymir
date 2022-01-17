from typing import Dict, Generator
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.config import settings


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
            json={"aliases": ["tabby", "kitten"]},
        )
        res = r.json()
        assert res["result"]["failed"] == ["tabby", "kitten"]
