import random

import pytest

from app.utils import graph as m
from tests.utils.utils import random_lower_string


class TestYmirNode:
    def test_create_ymir_node(self):
        d = {
            "id": random.randint(1000, 2000),
            "name": random_lower_string(10),
            "hash": random_lower_string(10),
            "label": "Model",
        }
        node = m.YmirNode.from_dict(d)
        assert node.label == "Model"
        assert node.id == d["id"]
        assert node.properties["name"] == d["name"]
        assert node.properties["hash"] == d["hash"]


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    mocker.patch.object(m, "StrictRedis")


class TestGraphClient:
    def test_query(self, mocker):
        mock_graph = mocker.Mock()
        mocker.patch.object(m, "Graph", return_value=mock_graph)
        q = random_lower_string()
        client = m.GraphClient(redis_uri=None)
        client.user_id = 2
        client.query(q)
        mock_graph.query.assert_called_with(q)

    def test_add_relationship(self, mocker):
        mock_graph = mocker.Mock()
        mocker.patch.object(m, "Graph", return_value=mock_graph)

        client = m.GraphClient(redis_uri=None)
        client.user_id = 2
        client.add_relationship(
            {"id": 1, "label": "Dataset"},
            {"id": 2, "label": "Model"},
            {"id": 3, "label": "Task"},
        )

        mock_graph.query.assert_called()
