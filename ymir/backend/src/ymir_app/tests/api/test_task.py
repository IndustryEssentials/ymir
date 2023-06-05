from datetime import datetime
import random
import time
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.api.api_v1.api import tasks as m
from app.config import settings
from app.utils.timeutil import convert_datetime_to_timestamp
from tests.utils.tasks import create_task


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
def mock_viz(mocker):
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
        r = client.get(f"{settings.API_V1_STR}/tasks/", params={"limit": 100}, headers=normal_user_token_headers)
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
        assert task.last_message_datetime is None

        data = {
            "user_id": 233,
            "hash": task_hash,
            "state": m.TaskState.running,
            "percent": 0.5,
            "timestamp": time.time(),
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
        task = crud.task.update_last_message_datetime(db, id=task.id, dt=datetime.utcnow())

        data = {
            "user_id": 233,
            "hash": task_hash,
            "state": m.TaskState.running,
            "percent": 0.5,
            "timestamp": convert_datetime_to_timestamp(task.last_message_datetime) - 1,
        }
        r = client.post(
            f"{settings.API_V1_STR}/tasks/status",
            headers=api_key_headers,
            json=data,
        )
        assert r.json()["code"] == m.ObsoleteTaskStatus.code
