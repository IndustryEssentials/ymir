import random
import time

from app.utils import ymir_viz as m
from tests.utils.utils import random_lower_string


class TestAsset:
    def test_create_asset(self, mocker):
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
        keyword_id_to_name = {i: random_lower_string() for i in range(100)}
        A = m.Asset.from_viz_res(asset_id, res, keyword_id_to_name=keyword_id_to_name)
        assert A.url == m.get_asset_url(asset_id)


class TestAssets:
    def test_assets(self):
        res = {
            "elements": [
                {
                    "asset_id": random_lower_string(),
                    "class_ids": [random.randint(1, 80) for _ in range(10)],
                }
            ],
            "class_ids_count": {},
            "ignored_labels": {"cat": 1},
            "total": random.randint(1000, 2000),
        }
        keyword_id_to_name = {i: random_lower_string() for i in range(100)}
        AS = m.Assets.from_viz_res(res, keyword_id_to_name)
        assert AS.total == res["total"]


class TestModel:
    def test_model(self):
        res = {
            "model_id": random_lower_string(),
            "model_mAP": random.randint(1, 100) / 100,
        }
        M = m.Model.from_viz_res(res)
        assert M.hash == res["model_id"]
        assert M.map == res["model_mAP"]


class TestVizClient:
    def test_get_viz_client(self):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        assert viz.host == host
        assert viz.session

    def test_get_assets(self, mocker):
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
            "class_ids_count": {},
            "ignored_labels": {"cat": 1},
            "total": random.randint(1000, 2000),
        }
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session
        user_id = random.randint(1000, 2000)
        task_id = random_lower_string()
        keyword_id_to_name = {i: random_lower_string() for i in range(100)}
        viz.config(user_id=user_id, branch_id=task_id, keyword_id_to_name=keyword_id_to_name)
        ret = viz.get_assets()
        assert isinstance(ret, m.Assets)
        assert ret.total
        assert ret.items

    def test_get_asset(self, mocker):
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
        task_id = random_lower_string()
        asset_id = random_lower_string()
        keyword_id_to_name = {i: random_lower_string() for i in range(100)}
        viz.config(user_id=user_id, branch_id=task_id, keyword_id_to_name=keyword_id_to_name)
        ret = viz.get_asset(asset_id=asset_id)
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
        }
        resp.json.return_value = {"result": res}
        mock_session.get.return_value = resp
        viz.session = mock_session

        user_id = random.randint(100, 200)
        task_id = random_lower_string()
        viz.config(user_id=user_id, branch_id=task_id)
        ret = viz.get_model()
        assert isinstance(ret, dict)
        assert ret["hash"] == res["model_id"]
        assert ret["map"] == res["model_mAP"]

    def test_close(self, mocker):
        host = random_lower_string()
        viz = m.VizClient(host=host)
        viz.session = mock_session = mocker.Mock()

        viz.close()
        mock_session.close.assert_called()
