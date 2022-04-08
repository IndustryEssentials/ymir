from random import randint
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from tests.utils.projects import create_project_record
from tests.utils.utils import random_lower_string


class TestListProjects:
    def test_list_projects_with_results(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        for _ in range(3):
            create_project_record(db, user_id)
        r = client.get(f"{settings.API_V1_STR}/projects/", headers=normal_user_token_headers)
        items = r.json()["result"]["items"]
        assert len(items) != 0


class TestCreateProject:
    def test_create_project(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        j = {
            "name": random_lower_string(),
            "training_keywords": ["kitten"],
        }
        r = client.post(
            f"{settings.API_V1_STR}/projects/",
            headers=normal_user_token_headers,
            json=j,
        )
        assert r.ok
        assert r.json()["result"]["training_dataset_group_id"] is not None


class TestGetProject:
    def test_get_project(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        record = create_project_record(db, user_id)
        r = client.get(
            f"{settings.API_V1_STR}/projects/{record.id}",
            headers=normal_user_token_headers,
            params={"project_id": record.id},
        )
        assert record.name == r.json()["result"]["name"]
        assert record.id == r.json()["result"]["id"]

    def test_get_project_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        project_id = randint(1000, 2000)
        r = client.get(
            f"{settings.API_V1_STR}/projects/{project_id}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404


class TestUpdateProject:
    def test_update_project(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        record = create_project_record(db, user_id)
        new_name = random_lower_string()
        r = client.patch(
            f"{settings.API_V1_STR}/projects/{record.id}",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.json()["result"]["name"] == new_name

    def test_update_project_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.patch(
            f"{settings.API_V1_STR}/projects/233333",
            headers=normal_user_token_headers,
            json={},
        )
        assert r.status_code == 404


class TestDeleteProject:
    def test_delete_project(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        group = create_project_record(db, user_id)
        assert not group.is_deleted
        r = client.delete(
            f"{settings.API_V1_STR}/projects/{group.id}",
            headers=normal_user_token_headers,
        )
        assert r.json()["result"]["is_deleted"]

    def test_delete_project_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.delete(f"{settings.API_V1_STR}/projects/233333", headers=normal_user_token_headers)
        assert r.status_code == 404
