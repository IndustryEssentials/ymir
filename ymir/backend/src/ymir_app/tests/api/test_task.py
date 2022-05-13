import random
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.api_v1.api import tasks as m
from app.config import settings
from tests.utils.tasks import create_task
from tests.utils.utils import random_lower_string


@pytest.fixture(scope="function")
def mock_controller(mocker):
    c = mocker.Mock()

    c.get_labels_of_user.return_value = {
        "cat": {
            "name": "cat",
            "aliases": [],
            "create_time": 1647075201.0,
            "update_time": 1647075202.0,
            "id": 0,
        },
        "dog": {
            "id": 1,
            "name": "dog",
            "aliases": ["puppy"],
            "create_time": 1647076203.0,
            "update_time": 1647076404.0,
        },
    }
    return c


@pytest.fixture(scope="function")
def mock_controller_request(mocker):
    r = mocker.Mock()
    mocker.patch.object(m, "ControllerRequest", return_value=r)


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
def mock_clickhouse(mocker):
    return mocker.Mock()


class TestListTasks:
    def test_list_tasks_succeed(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_controller,
    ):
        for _ in range(3):
            create_task(db, user_id)
        r = client.get(f"{settings.API_V1_STR}/tasks/", headers=normal_user_token_headers)
        items = r.json()["result"]["items"]
        total = r.json()["result"]["total"]
        assert len(items) == total != 0


class TestDeleteTask:
    def test_delete_task(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        mock_controller,
        user_id: int,
    ):
        task = create_task(db, user_id)
        task_id = task.id
        r = client.delete(f"{settings.API_V1_STR}/tasks/{task_id}", headers=normal_user_token_headers)
        assert r.json()["result"]["is_deleted"]


class TestChangeTaskName:
    def test_change_task_name(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        mock_controller,
        user_id: int,
    ):
        task = create_task(db, user_id)
        old_name = task.name
        task_id = task.id
        new_name = random_lower_string(5)
        r = client.patch(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.json()["result"]["name"] == new_name != old_name


class TestGetTask:
    def test_get_single_task(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        mock_controller,
        user_id: int,
    ):
        task = create_task(db, user_id)
        name = task.name
        task_id = task.id

        r = client.get(f"{settings.API_V1_STR}/tasks/{task_id}", headers=normal_user_token_headers)
        assert r.json()["result"]["name"] == name

    def test_get_single_task_not_found(self, client: TestClient, normal_user_token_headers, mocker):
        task_id = random.randint(100000, 900000)
        r = client.get(f"{settings.API_V1_STR}/tasks/{task_id}", headers=normal_user_token_headers)
        assert r.status_code == 404


class TestTerminateTask:
    def test_terminate_task_discard_result(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        mock_controller,
        user_id: int,
    ):
        task = create_task(db, user_id)
        task_id = task.id
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/terminate",
            headers=normal_user_token_headers,
            json={"fetch_result": False},
        )
        assert r.json()["result"]["state"] == m.TaskState.terminate.value

    def test_terminate_task_keep_result(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers,
        mocker,
        mock_controller,
        user_id: int,
    ):
        task = create_task(db, user_id)
        task_id = task.id
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/terminate",
            headers=normal_user_token_headers,
            json={"fetch_result": True},
        )
        # Note that we map premature back to terminate for frontend
        assert r.json()["result"]["state"] == m.TaskState.terminate.value


class TestUpdateTaskStatus:
    def test_update_task_status_to_done(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers,
        api_key_headers,
        mocker,
        mock_controller,
        user_id: int,
    ):
        task = create_task(db, user_id)
        task_hash = task.hash
        last_message_datetime = task.last_message_datetime

        data = {
            "user_id": 233,
            "hash": task_hash,
            "state": m.TaskState.running,
            "percent": 0.5,
            "timestamp": m.convert_datetime_to_timestamp(last_message_datetime) + 1,
        }
        r = client.post(
            f"{settings.API_V1_STR}/tasks/status",
            headers=api_key_headers,
            json=data,
        )
        assert r.json()["result"]["state"] == m.TaskState.running.value
        assert r.json()["result"]["percent"] == 0.5

    def test_update_task_status_skip_obsolete_msg(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers,
        api_key_headers,
        mocker,
        mock_controller,
        user_id: int,
    ):
        task = create_task(db, user_id)
        task_hash = task.hash
        last_message_datetime = task.last_message_datetime

        data = {
            "user_id": 233,
            "hash": task_hash,
            "state": m.TaskState.running,
            "percent": 0.5,
            "timestamp": m.convert_datetime_to_timestamp(last_message_datetime) - 1,
        }
        r = client.post(
            f"{settings.API_V1_STR}/tasks/status",
            headers=api_key_headers,
            json=data,
        )
        assert r.json()["code"] == m.ObsoleteTaskStatus.code
