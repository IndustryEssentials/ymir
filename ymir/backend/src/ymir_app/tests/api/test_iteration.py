from random import randint
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from tests.utils.iterations import create_iteration_record


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
