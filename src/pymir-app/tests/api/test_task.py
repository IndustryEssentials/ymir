import random
from typing import Dict

import pytest
from fastapi.testclient import TestClient

from app.api.api_v1.api import tasks as m
from app.config import settings
from tests.utils.utils import random_lower_string


@pytest.fixture(scope="function")
def mock_controller(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def mock_db(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def mock_graph_db(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def mock_viz(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def mock_stats(mocker):
    return mocker.Mock()


class TestTaskResult:
    def test_get_task_result(
        self, mocker, mock_controller, mock_db, mock_graph_db, mock_viz
    ):
        task_result_proxy = m.TaskResultProxy(
            controller=mock_controller,
            db=mock_db,
            graph_db=mock_graph_db,
            viz=mock_viz,
            stats_client=mock_stats,
        )
        user_id = random.randint(1000, 2000)
        task_hash = random_lower_string(32)
        task_result_proxy.parse_resp = mocker.Mock(
            return_value={"state": m.TaskState.done, "task_id": task_hash}
        )
        task = mocker.Mock(hash=task_hash)
        mocker.patch.object(m, "ControllerRequest", return_value=None)
        result = task_result_proxy.get(task)
        mock_controller.send.assert_called()

    def test_save_task_result(self, mocker, mock_controller, mock_db, mock_graph_db):
        task_result_proxy = m.TaskResultProxy(
            controller=mock_controller,
            db=mock_db,
            graph_db=mock_graph_db,
            viz=mock_viz,
            stats_client=mock_stats,
        )
        task_result_proxy.get = mocker.Mock()
        task_hash = random_lower_string(32)
        task_result_proxy.parse_resp = mocker.Mock(
            return_value={"state": m.TaskState.done, "task_id": task_hash}
        )
        task_result_proxy.send_notification = mocker.Mock()
        task_result_proxy.add_new_model_if_not_exist = mocker.Mock()
        task_result_proxy.add_new_dataset_if_not_exist = mocker.Mock()

        task = mocker.Mock(type=m.TaskType.training)
        task_result_proxy.update_task_progress = mocker.Mock(return_value=task)

        user_id = random.randint(1000, 2000)
        task_hash = random_lower_string(32)
        task = mocker.Mock(hash=task_hash)
        mocker.patch.object(m, "ControllerRequest", return_value=None)
        result = task_result_proxy.get(task)
        task_result_proxy.save(task, result)

    def test_get_dataset_info(self, mocker, mock_controller, mock_db, mock_graph_db):
        viz = mocker.Mock()
        keywords = {"a": 1, "b": 2, "c": 3, "d": 4}
        items = list(range(random.randint(10, 100)))
        viz.get_assets.return_value = mocker.Mock(
            keywords=keywords, items=items, total=len(items)
        )
        proxy = m.TaskResultProxy(
            controller=mock_controller,
            db=mock_db,
            graph_db=mock_graph_db,
            viz=viz,
            stats_client=mock_stats,
        )
        user_id = random.randint(1000, 2000)
        task_hash = random_lower_string(32)
        result = proxy.get_dataset_info(user_id, task_hash)
        assert result["keywords"] == list(keywords.keys())


def test_get_default_dataset_name():
    task_hash = random_lower_string(32)
    task_name = random_lower_string(10)
    assert m.get_default_record_name(task_hash, task_name) == task_name + "_" + task_hash[-6:]


class TestNormalizeParameters:
    def test_normalize_task_parameters_succeed(self, mocker):
        mocker.patch.object(m, "crud")
        params = {
            "include_classes": [],
            "include_datasets": [1, 2, 3],
            "model_id": 233,
            "name": random_lower_string(5),
            "else": None,
        }
        params = m.schemas.TaskParameter(**params)
        res = m.normalize_parameters(mocker.Mock(), random_lower_string(5), params)
        assert "include_classes" in res
        assert "include_datasets" in res
        assert "model_hash" in res

    def test_normalize_task_parameters_skip(self, mocker):
        assert (
            m.normalize_parameters(mocker.Mock(), random_lower_string(5), None) is None
        )


class TestUpdateStats:
    user_id = "0233"

    def test_update_stats_only_update_task_stats(self, mocker):
        stats = mocker.Mock()
        task = mocker.Mock(parameters=None)
        m.update_stats(self.user_id, stats, task)
        stats.update_task_stats.assert_called()
        stats.update_model_rank.assert_not_called()

    def test_update_stats_for_model(self, mocker):
        stats = mocker.Mock()
        task = mocker.Mock(parameters={"model_id": 1})
        m.update_stats(self.user_id, stats, task)
        stats.update_model_rank.assert_called_with(self.user_id, 1)

    def test_update_stats_for_dataset(self, mocker):
        stats = mocker.Mock()
        task = mocker.Mock(parameters={"datasets": [233]})
        m.update_stats(self.user_id, stats, task)
        stats.update_dataset_rank.assert_called_with(self.user_id, 233)


def create_task(client, headers):
    j = {
        "name": random_lower_string(),
        "type": m.TaskType.mining,
    }
    r = client.post(f"{settings.API_V1_STR}/tasks/", headers=headers, json=j)

    return r


class TestListTasks:
    def test_list_tasks_succeed(
        self, client: TestClient, normal_user_token_headers: Dict[str, str], mocker
    ):
        req = mocker.Mock(task_id="task_id_233")
        mocker.patch.object(m, "ControllerRequest", return_value=req)
        for _ in range(3):
            r = create_task(client, normal_user_token_headers)
        r = client.get(
            f"{settings.API_V1_STR}/tasks/", headers=normal_user_token_headers
        )
        items = r.json()["result"]["items"]
        total = r.json()["result"]["total"]
        assert len(items) == total != 0


class TestDeleteTask:
    def test_delete_task(self, client: TestClient, normal_user_token_headers, mocker):
        req = mocker.Mock(task_id="task_id_233")
        mocker.patch.object(m, "ControllerRequest", return_value=req)
        r = create_task(client, normal_user_token_headers)
        assert not r.json()["result"]["is_deleted"]
        task_id = r.json()["result"]["id"]
        r = client.delete(
            f"{settings.API_V1_STR}/tasks/{task_id}", headers=normal_user_token_headers
        )
        assert r.json()["result"]["is_deleted"]


class TestChangeTaskName:
    def test_change_task_name(
        self, client: TestClient, normal_user_token_headers, mocker
    ):
        req = mocker.Mock(task_id="task_id_233")
        mocker.patch.object(m, "ControllerRequest", return_value=req)
        r = create_task(client, normal_user_token_headers)
        old_name = r.json()["result"]["name"]
        task_id = r.json()["result"]["id"]
        new_name = random_lower_string(5)
        r = client.patch(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.json()["result"]["name"] == new_name != old_name


class TestGetTask:
    def test_get_single_task(
        self, client: TestClient, normal_user_token_headers, mocker
    ):
        req = mocker.Mock(task_id="task_id_233")
        mocker.patch.object(m, "ControllerRequest", return_value=req)
        r = create_task(client, normal_user_token_headers)
        name = r.json()["result"]["name"]
        task_id = r.json()["result"]["id"]

        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}", headers=normal_user_token_headers
        )
        assert r.json()["result"]["name"] == name

    def test_get_single_task_not_found(
        self, client: TestClient, normal_user_token_headers, mocker
    ):
        task_id = 2333
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}", headers=normal_user_token_headers
        )
        r.status_code == 404
