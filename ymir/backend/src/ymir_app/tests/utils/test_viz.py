import random
import time
from typing import Dict

import pytest

from app.utils import ymir_viz as m
from common_utils.labels import UserLabels
from tests.utils.utils import random_lower_string


@pytest.fixture(scope="module")
def mock_user_labels() -> Dict:
    user_labels = []
    for i in range(100):
        name = random_lower_string()
        user_labels.append(
            {
                "name": name,
                "aliases": [],
                "create_time": 1647075222.0,
                "update_time": 1647075211.0,
                "id": i,
            }
        )

    return UserLabels.parse_obj(dict(labels=user_labels))


class TestAsset:
    def test_create_asset(self, mock_user_labels, mocker):
        asset_id = random_lower_string()
        res = {
            "asset_id": asset_id,
            "pred": [
                {
                    "box": {},
                    "class_id": random.randint(1, 20),
                    "cm": 1,
                    "tags": {},
                    "mask": random_lower_string(),
                    "polygon": [random.randint(100, 200)],
                }
            ],
            "cks": [],
            "gt": [
                {
                    "box": {},
                    "class_id": random.randint(1, 20),
                    "cm": 1,
                    "tags": {},
                    "mask": random_lower_string(),
                    "polygon": [random.randint(100, 200)],
                }
            ],
            "class_ids": list(range(1, 20)),
            "metadata": {
                "height": random.randint(100, 200),
                "width": random.randint(100, 200),
                "image_channels": random.randint(1, 3),
                "timestamp": {"start": time.time()},
            },
        }

        A = m.ViewerAsset(
            res["asset_id"],
            res["class_ids"],
            res["metadata"],
            res["gt"],
            res["pred"],
            res["cks"],
            user_labels=mock_user_labels,
        )
        assert A.url == m.get_asset_url(asset_id)


class TestAssets:
    def test_assets(self, mock_user_labels):
        res = {
            "elements": [
                {
                    "asset_id": random_lower_string(),
                    "class_ids": [random.randint(1, 80) for _ in range(10)],
                    "pred": [
                        {
                            "box": {},
                            "class_id": random.randint(1, 20),
                            "cm": 1,
                            "tags": {},
                            "mask": random_lower_string(),
                            "polygon": [random.randint(100, 200)],
                        }
                    ],
                    "gt": [
                        {
                            "box": {},
                            "class_id": random.randint(1, 20),
                            "cm": 1,
                            "tags": {},
                            "mask": random_lower_string(),
                            "polygon": [random.randint(100, 200)],
                        }
                    ],
                    "metadata": {
                        "height": random.randint(100, 200),
                        "width": random.randint(100, 200),
                        "image_channels": random.randint(1, 3),
                        "timestamp": {"start": time.time()},
                    },
                    "cks": {},
                }
            ],
            "total_assets_count": 124,
        }
        AS = m.ViewerAssetsResponse(res["total_assets_count"], res["elements"], user_labels=mock_user_labels)
        assert len(AS.items) == len(res["elements"])


class TestModel:
    def test_model(self):
        res = {
            "model_hash": random_lower_string(),
            "mAP": random.randint(1, 100) / 100,
            "task_parameters": "mock_task_parameters",
            "executor_config": {"class_names": "a,b,c".split(",")},
            "stages": {
                "epoch-1000": {
                    "mAP": -1,
                    "timestamp": 100000000,
                },
                "epoch-2000": {
                    "mAP": 0.3,
                    "timestamp": 100000001,
                },
                "epoch-3000": {
                    "mAP": 0.83,
                    "timestamp": 100000002,
                },
            },
            "best_stage_name": "epoch-3000",
            "object_type": 2,
        }
        M = m.ViewerModelInfoResponse.parse_obj(res)
        assert M.hash == res["model_hash"]
        assert M.map == res["mAP"]
        assert M.task_parameters == res["task_parameters"]
        assert M.executor_config == res["executor_config"]
        assert M.model_stages == res["stages"]
        assert M.best_stage_name == res["best_stage_name"]


class TestDataset:
    def test_dataset(self, mock_user_labels):
        res = {
            "class_ids_count": {3: 34},
            "new_types": {"cat": 5},
            "new_types_added": False,
            "evaluation_state": 4,
            "cks_count_total": {},
            "cks_count": {},
            "total_assets_count": 1,
            "pred": {
                "class_ids_count": {3: 34},
                "class_obj_count": {3: 34},
                "class_ids_mask_area": {3: 23},
                "new_types": {"cat": 5},
                "new_types_added": False,
                "negative_assets_count": 0,
                "tags_count_total": {},
                "tags_count": {},
                "annos_count": 28,
                "class_names_count": {"cat": 3},
                "hist": {"anno_area_ratio": [[{"x": 1, "y": 2}]], "anno_quality": [[{"x": 1, "y": 2}]]},
            },
            "gt": {},
            "hist": {
                "asset_area": [[{"x": 1, "y": 2}]],
                "asset_bytes": [[{"x": 1, "y": 2}]],
                "asset_hw_ratio": [[{"x": 1, "y": 2}]],
                "asset_quality": [[{"x": 1, "y": 2}]],
            },
            "cks": {},
            "total_assets_mbytes": 10,
            "total_assets_count": 1,
        }
        M = m.DatasetInfo.from_dict(res, mock_user_labels)
        assert "gt" in M.keywords
        assert "pred" in M.keywords
        assert M.gt is None
        assert M.pred


class TestVizClient:
    def test_get_viz_client(self):
        viz = m.VizClient()
        assert viz.session

    def test_get_assets(self, mock_user_labels, mocker):
        viz = m.VizClient()
        mock_session = mocker.Mock()
        resp = mocker.Mock()
        res = {
            "elements": [
                {
                    "asset_id": random_lower_string(),
                    "class_ids": [random.randint(1, 80) for _ in range(10)],
                    "pred": [
                        {
                            "box": {},
                            "class_id": random.randint(1, 20),
                            "cm": 1,
                            "tags": {},
                            "mask": random_lower_string(),
                            "polygon": [random.randint(100, 200)],
                        }
                    ],
                    "gt": [
                        {
                            "box": {},
                            "class_id": random.randint(1, 20),
                            "cm": 1,
                            "tags": {},
                            "mask": random_lower_string(),
                            "polygon": [random.randint(100, 200)],
                        }
                    ],
                    "metadata": {
                        "height": random.randint(100, 200),
                        "width": random.randint(100, 200),
                        "image_channels": random.randint(1, 3),
                        "timestamp": {"start": time.time()},
                    },
                    "cks": {},
                }
            ],
            "total_assets_count": random.randint(1000, 2000),
        }
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session
        user_id = random.randint(1000, 2000)
        project_id = random.randint(1000, 2000)
        task_id = random_lower_string()
        viz.initialize(
            user_id=user_id,
            project_id=project_id,
            user_labels=mock_user_labels,
        )
        ret = viz.get_assets(dataset_hash=task_id)
        assert isinstance(ret, Dict)
        assert ret["total"]
        assert ret["items"]
        assert len(ret["items"]) == len(res["elements"])

    def test_get_model_info(self, mocker):
        viz = m.VizClient()
        mock_session = mocker.Mock()
        resp = mocker.Mock()
        res = {
            "model_hash": random_lower_string(),
            "mAP": random.randint(1, 100) / 100,
            "task_parameters": "mock_task_parameters",
            "executor_config": {"class_names": "a,b,c".split(",")},
            "stages": {
                "epoch-1000": {
                    "mAP": -1,
                    "timestamp": 100000000,
                },
                "epoch-2000": {
                    "mAP": 0.3,
                    "timestamp": 100000001,
                },
                "epoch-3000": {
                    "mAP": 0.83,
                    "timestamp": 100000002,
                },
            },
            "best_stage_name": "epoch-3000",
            "object_type": 2,
        }
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session

        user_id = random.randint(100, 200)
        project_id = random.randint(100, 200)
        task_id = random_lower_string()
        viz.initialize(user_id=user_id, project_id=project_id)
        ret = viz.get_model_info(task_id)
        assert isinstance(ret, Dict)
        assert ret["hash"] == res["model_hash"]
        assert ret["map"] == res["mAP"]
        assert ret["task_parameters"] == res["task_parameters"]
        assert ret["executor_config"] == res["executor_config"]

    def test_get_dataset_analysis(self, mock_user_labels, mocker):
        viz = m.VizClient()
        mock_session = mocker.Mock()
        resp = mocker.Mock()
        res = {
            "class_ids_count": {3: 34},
            "new_types": {"cat": 5},
            "new_types_added": False,
            "evaluation_state": 4,
            "cks_count_total": {},
            "cks_count": {},
            "total_assets_count": 1,
            "pred": {
                "class_ids_count": {3: 34},
                "class_obj_count": {3: 34},
                "class_ids_mask_area": {3: 23},
                "new_types": {"cat": 5},
                "new_types_added": False,
                "tags_count_total": {},
                "tags_count": {},
                "negative_assets_count": 0,
                "annos_count": 28,
                "class_names_count": {"cat": 3},
                "hist": {"anno_area_ratio": [[{"x": 1, "y": 2}]], "anno_quality": [[{"x": 1, "y": 2}]]},
            },
            "gt": {},
            "hist": {
                "asset_area": [[{"x": 1, "y": 2}]],
                "asset_bytes": [[{"x": 1, "y": 2}]],
                "asset_hw_ratio": [[{"x": 1, "y": 2}]],
                "asset_quality": [[{"x": 1, "y": 2}]],
            },
            "total_assets_mbytes": 10,
            "total_assets_count": 1,
            "cks": {},
        }
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session

        user_id = random.randint(100, 200)
        project_id = random.randint(100, 200)
        task_id = random_lower_string()
        viz.initialize(user_id=user_id, project_id=project_id, user_labels=mock_user_labels)
        ret = viz.get_dataset_analysis(dataset_hash=task_id)
        assert isinstance(ret, Dict)
        assert "gt" in ret["keywords"]
        assert "pred" in ret["keywords"]
        assert ret["gt"] is None
        assert ret["pred"]

    def test_close(self, mocker):
        viz = m.VizClient()
        viz.session = mock_session = mocker.Mock()

        viz.close()
        mock_session.close.assert_called()
