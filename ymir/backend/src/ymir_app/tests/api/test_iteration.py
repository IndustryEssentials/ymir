from random import randint
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from id_definition.error_codes import APIErrorCode as error_codes
from tests.utils.iterations import create_iteration_record, create_iteration_via_api
from tests.utils.tasks import create_task


class TestCreateIteration:
    def test_create_iteration(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        assert iteration["user_id"] == user_id


class TestListIterations:
    def test_list_iterations_with_results(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        project_id = randint(1000, 2000)
        for _ in range(3):
            create_iteration_record(db, user_id, project_id)
        r = client.get(
            f"{settings.API_V1_STR}/iterations/", headers=normal_user_token_headers, params={"project_id": project_id}
        )
        items = r.json()["result"]
        assert len(items) == 3


class TestGetIteration:
    def test_get_iteration(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        project_id = randint(1000, 2000)
        record = create_iteration_record(db, user_id)
        r = client.get(
            f"{settings.API_V1_STR}/iterations/{record.id}",
            headers=normal_user_token_headers,
            params={"project_id": project_id},
        )
        assert record.project_id == r.json()["result"]["project_id"]
        assert record.id == r.json()["result"]["id"]

    def test_get_iteration_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        project_id = randint(1000, 2000)
        r = client.get(
            f"{settings.API_V1_STR}/iterations/233333",
            headers=normal_user_token_headers,
            params={"project_id": project_id},
        )
        assert r.status_code == 404


class TestUpdateIteration:
    def test_update_iteration(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        record = create_iteration_record(db, user_id)
        r = client.patch(
            f"{settings.API_V1_STR}/iterations/{record.id}",
            headers=normal_user_token_headers,
            json={"current_stage": 3},
        )
        assert r.json()["result"]["current_stage"] == 3

    def test_update_iteration_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.patch(
            f"{settings.API_V1_STR}/iterations/233333",
            headers=normal_user_token_headers,
            json={"current_stage": 3},
        )
        assert r.status_code == 404


class TestListIterationStep:
    def test_list_steps(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]

        r = client.get(f"{settings.API_V1_STR}/iterations/{iteration_id}/steps", headers=normal_user_token_headers)
        items = r.json()["result"]
        assert len(items) == 5

    def test_list_steps_iteration_not_found(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration_id = randint(1000, 2000)
        r = client.get(f"{settings.API_V1_STR}/iterations/{iteration_id}/steps", headers=normal_user_token_headers)
        assert r.json()["code"] == error_codes.ITERATION_NOT_FOUND


class TestGetIterationStep:
    def test_get_step(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        step_name = iteration["current_step"]["name"]
        r = client.get(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}", headers=normal_user_token_headers
        )
        assert r.json()["result"]["name"] == step_name

    def test_get_step_iteration_not_found(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration_id, step_id = randint(1000, 2000), randint(1000, 2000)
        r = client.get(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}", headers=normal_user_token_headers
        )
        assert r.json()["code"] == error_codes.ITERATION_NOT_FOUND

    def test_get_step_not_found(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]

        step_id = randint(1000, 2000)
        r = client.get(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}", headers=normal_user_token_headers
        )
        assert r.json()["code"] == error_codes.ITERATION_STEP_NOT_FOUND


class TestBindStep:
    def test_bind_step(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        task = create_task(db, user_id)

        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        iteration["current_step"]["name"]

        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/bind",
            headers=normal_user_token_headers,
            params={"task_id": task.id},
        )
        assert r.json()["result"]["task_id"] == task.id

    def test_bind_step_task_not_found(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        task_id = randint(1000, 2000)
        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/bind",
            headers=normal_user_token_headers,
            params={"task_id": task_id},
        )
        assert r.json()["code"] == error_codes.TASK_NOT_FOUND

    def test_bind_finished_step(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        task = create_task(db, user_id)

        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        iteration["current_step"]["name"]

        client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/finish", headers=normal_user_token_headers
        )

        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/bind",
            headers=normal_user_token_headers,
            params={"task_id": task.id},
        )
        assert r.json()["code"] == error_codes.ITERATION_STEP_ALREADY_FINISHED


class TestUnbindStep:
    def test_unbind_step(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        task = create_task(db, user_id)

        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        iteration["current_step"]["name"]

        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/bind",
            headers=normal_user_token_headers,
            params={"task_id": task.id},
        )
        assert r.json()["result"]["task_id"] == task.id

        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/unbind",
            headers=normal_user_token_headers,
            params={"task_id": task.id},
        )
        assert not r.json()["result"]["task_id"]

    def test_unbind_finished_step(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        task = create_task(db, user_id)

        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        iteration["current_step"]["name"]

        client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/finish", headers=normal_user_token_headers
        )

        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/unbind",
            headers=normal_user_token_headers,
            params={"task_id": task.id},
        )
        assert r.json()["code"] == error_codes.ITERATION_STEP_ALREADY_FINISHED


class TestFinishStep:
    def test_finish_step(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/finish", headers=normal_user_token_headers
        )
        assert r.json()["result"]["is_finished"]

    def test_finish_step_iteration_not_found(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration_id, step_id = randint(1000, 2000), randint(1000, 2000)
        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/finish", headers=normal_user_token_headers
        )
        assert r.json()["code"] == error_codes.ITERATION_NOT_FOUND

    def test_finish_step_not_found(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = randint(1000, 2000)
        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/finish", headers=normal_user_token_headers
        )
        assert r.json()["code"] == error_codes.ITERATION_STEP_NOT_FOUND

    def test_finish_step_already_finished(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        iteration = create_iteration_via_api(db, client, user_id, normal_user_token_headers)
        iteration["project_id"]
        iteration_id = iteration["id"]
        step_id = iteration["current_step"]["id"]
        client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/finish", headers=normal_user_token_headers
        )

        r = client.post(
            f"{settings.API_V1_STR}/iterations/{iteration_id}/steps/{step_id}/finish", headers=normal_user_token_headers
        )
        assert r.json()["code"] == error_codes.ITERATION_STEP_ALREADY_FINISHED
