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
            "annotations": [
                {
                    "box": random_lower_string(10),
                    "class_id": random.randint(1, 20),
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

        A = m.Asset.from_viz_res(asset_id, res, user_labels=mock_user_labels)
        assert A.url == m.get_asset_url(asset_id)


class TestAssets:
    def test_assets(self, mock_user_labels):
        res = {
            "elements": [
                {
                    "asset_id": random_lower_string(),
                    "class_ids": [random.randint(1, 80) for _ in range(10)],
                }
            ],
            "total": 124,
        }
        AS = m.Assets.from_viz_res(res, mock_user_labels)
        assert len(AS.items) == len(res["elements"])


class TestModel:
    def test_model(self):
        res = {
            "model_id": random_lower_string(),
            "model_mAP": random.randint(1, 100) / 100,
            "task_parameters": "mock_task_parameters",
            "executor_config": "mock_executor_config",
        }
        M = m.ModelMetaData.from_viz_res(res)
        assert M.hash == res["model_id"]
        assert M.map == res["model_mAP"]
        assert M.task_parameters == res["task_parameters"]
        assert M.executor_config == res["executor_config"]


class TestDataset:
    def test_dataset(self, mock_user_labels):
        res = {
            "class_ids_count": {3: 34},
            "ignored_labels": {"cat": 5},
            "negative_info": {"negative_images_cnt": 0, "project_negative_images_cnt": 0},
            "total_images_cnt": 1,
        }
        M = m.DatasetMetaData.from_viz_res(res, mock_user_labels)
        assert M.keyword_count == len(res["class_ids_count"])
        assert M.ignored_keywords == res["ignored_labels"]
        assert M.negative_info["negative_images_cnt"] == res["negative_info"]["negative_images_cnt"]
        assert M.negative_info["project_negative_images_cnt"] == res["negative_info"]["project_negative_images_cnt"]
        assert M.asset_count == res["total_images_cnt"]


class TestVizClient:
    def test_get_viz_client(self):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        assert viz.host == host
        assert viz.session

    def test_get_assets(self, mock_user_labels, mocker):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        mock_session = mocker.Mock()
        resp = mocker.Mock()
        res = {
            "elements": [
                {
                    "asset_id": random_lower_string(),
                    "class_ids": [random.randint(1, 80) for _ in range(10)],
                }
            ],
            "total": random.randint(1000, 2000),
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
            branch_id=task_id,
        )
        ret = viz.get_assets(user_labels=mock_user_labels)
        assert isinstance(ret, m.Assets)
        assert ret.total
        assert ret.items
        assert len(ret.items) == len(res["elements"])

    def test_get_asset(self, mock_user_labels, mocker):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        mock_session = mocker.Mock()
        resp = mocker.Mock()
        res = {
            "annotations": [
                {
                    "box": random_lower_string(10),
                    "class_id": random.randint(1, 80),
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
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session

        user_id = random.randint(100, 200)
        project_id = random.randint(100, 200)
        task_id = random_lower_string()
        asset_id = random_lower_string()
        viz.initialize(
            user_id=user_id,
            project_id=project_id,
            branch_id=task_id,
        )
        ret = viz.get_asset(asset_id=asset_id, user_labels=mock_user_labels)
        assert isinstance(ret, dict)
        assert ret["hash"] == asset_id

    def test_get_model(self, mocker):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        mock_session = mocker.Mock()
        resp = mocker.Mock()
        res = {
            "model_id": random_lower_string(),
            "model_mAP": random.randint(1, 100) / 100,
            "task_parameters": "mock_task_parameters",
            "executor_config": "mock_executor_config",
        }
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session

        user_id = random.randint(100, 200)
        project_id = random.randint(100, 200)
        task_id = random_lower_string()
        viz.initialize(user_id=user_id, project_id=project_id, branch_id=task_id)
        ret = viz.get_model()
        assert isinstance(ret, m.ModelMetaData)
        assert ret.hash == res["model_id"]
        assert ret.map == res["model_mAP"]
        assert ret.task_parameters == res["task_parameters"]
        assert ret.executor_config == res["executor_config"]

    def test_get_dataset(self, mock_user_labels, mocker):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        mock_session = mocker.Mock()
        resp = mocker.Mock()
        res = {
            "class_ids_count": {3: 34},
            "ignored_labels": {"cat": 5},
            "negative_info": {"negative_images_cnt": 0, "project_negative_images_cnt": 0},
            "total_images_cnt": 1,
        }
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session

        user_id = random.randint(100, 200)
        project_id = random.randint(100, 200)
        task_id = random_lower_string()
        viz.initialize(user_id=user_id, project_id=project_id, branch_id=task_id)
        ret = viz.get_dataset(mock_user_labels)
        assert isinstance(ret, m.DatasetMetaData)
        assert ret.keyword_count == len(res["class_ids_count"])
        assert ret.ignored_keywords == res["ignored_labels"]
        assert ret.negative_info["negative_images_cnt"] == res["negative_info"]["negative_images_cnt"]
        assert ret.negative_info["project_negative_images_cnt"] == res["negative_info"]["project_negative_images_cnt"]
        assert ret.asset_count == res["total_images_cnt"]

    def test_close(self, mocker):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        viz.session = mock_session = mocker.Mock()

        viz.close()
        mock_session.close.assert_called()
