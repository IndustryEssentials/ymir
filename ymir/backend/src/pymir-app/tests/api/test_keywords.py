from typing import Dict, Generator
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api import deps
from app.config import settings
from app.main import app


def fake_controller_client() -> Generator:
    try:
        client = Mock()
        client.send.return_value = {"csv_labels": ["tabby", "kitten"]}
        yield client
    finally:
        client.close()


app.dependency_overrides[deps.get_controller_client] = fake_controller_client


class TestUpdateKeyword:

    def test_update_keyword(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.patch(
            f"{settings.API_V1_STR}/keywords/cat", headers=normal_user_token_headers, json={"aliases": ["tabby", "kitten"]},
        )
        res = r.json()
        assert res["result"]["failed"] == ["tabby", "kitten"]

