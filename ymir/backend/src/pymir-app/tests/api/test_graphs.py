from typing import Dict

from fastapi.testclient import TestClient

from app.api.api_v1.api import graphs as m
from app.config import settings


class TestGetGraph:
    def test_get_graph_for_model_node(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        crud = mocker.Mock()
        crud.model.get.return_value = mocker.Mock()
        mocker.patch.object(m, "crud", return_value=crud)
        r = client.get(
            f"{settings.API_V1_STR}/graphs/",
            headers=normal_user_token_headers,
            params={"type": "model", "id": 1},
        )
        result = r.json()["result"]
        assert "nodes" in result
        assert "edges" in result
