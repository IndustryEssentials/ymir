from random import randint
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from tests.utils.models import create_model_group_record, create_model
from tests.utils.utils import random_lower_string


class TestListModelGroups:
    def test_list_model_groups_with_results(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        project_id = randint(1000, 2000)
        for _ in range(3):
            grp = create_model_group_record(db, user_id, project_id)
            create_model(db, user_id, grp.id)
        r = client.get(
            f"{settings.API_V1_STR}/model_groups/", headers=normal_user_token_headers, params={"project_id": project_id}
        )
        items = r.json()["result"]["items"]
        total = r.json()["result"]["total"]
        assert len(items) == total == 3


class TestDeleteModelGroup:
    def test_delete_model_group(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        group = create_model_group_record(db, user_id)
        assert not group.is_deleted
        r = client.delete(
            f"{settings.API_V1_STR}/model_groups/{group.id}",
            headers=normal_user_token_headers,
        )
        assert r.json()["result"]["is_deleted"]

    def test_delete_model_group_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.delete(f"{settings.API_V1_STR}/model_groups/233333", headers=normal_user_token_headers)
        assert r.status_code == 404


class TestGetModelGroup:
    def test_get_model_group(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        group = create_model_group_record(db, user_id)
        r = client.get(
            f"{settings.API_V1_STR}/model_groups/{group.id}",
            headers=normal_user_token_headers,
        )
        assert group.project_id == r.json()["result"]["project_id"]
        assert group.id == r.json()["result"]["id"]

    def test_get_model_group_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.get(f"{settings.API_V1_STR}/model_groups/233333", headers=normal_user_token_headers)
        assert r.status_code == 404


class TestRenameModelGroup:
    def test_rename_model_group(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        group = create_model_group_record(db, user_id)
        new_name = random_lower_string()
        r = client.patch(
            f"{settings.API_V1_STR}/model_groups/{group.id}",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.json()["result"]["name"] == new_name

    def test_rename_model_group_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.patch(
            f"{settings.API_V1_STR}/model_groups/233333",
            headers=normal_user_token_headers,
            json={"name": random_lower_string()},
        )
        assert r.status_code == 404
