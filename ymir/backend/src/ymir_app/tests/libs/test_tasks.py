from typing import Any
from app.libs import tasks as m
from tests.utils.utils import random_lower_string
from common_utils.labels import UserLabels


class TestNormalizeParameters:
    def test_normalize_task_parameters_succeed(self, mocker: Any) -> Any:
        mocker.patch.object(m, "crud")
        params = {
            "keywords": "cat,dog,boy".split(","),
            "dataset_id": 1,
            "model_id": 233,
            "name": random_lower_string(5),
            "else": None,
        }
        user_labels = UserLabels.parse_obj(
            dict(
                labels=[
                    {
                        "name": "cat",
                        "aliases": [],
                        "create_time": 1647075205.0,
                        "update_time": 1647075206.0,
                        "id": 0,
                    },
                    {
                        "id": 1,
                        "name": "dog",
                        "aliases": [],
                        "create_time": 1647076207.0,
                        "update_time": 1647076408.0,
                    },
                    {
                        "id": 2,
                        "name": "boy",
                        "aliases": [],
                        "create_time": 1647076209.0,
                        "update_time": 1647076410.0,
                    },
                ]
            )
        )
        params = m.schemas.TaskParameter(**params)
        res = m.normalize_parameters(mocker.Mock(), params, None, user_labels)
        assert res["class_ids"] == [0, 1, 2]
        assert "dataset_hash" in res
        assert "model_hash" in res
