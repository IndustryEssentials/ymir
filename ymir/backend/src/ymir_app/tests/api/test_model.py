from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from tests.utils.models import create_model
from tests.utils.projects import create_project_record
from tests.utils.utils import random_lower_string


class TestListModels:
    def test_list_models_having_results(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        for _ in range(3):
            create_model(db, user_id)
        r = client.get(f"{settings.API_V1_STR}/models/", headers=normal_user_token_headers)
        datasets = r.json()["result"]["items"]
        total = r.json()["result"]["total"]
        assert len(datasets) == total != 0


class TestBatchGetModels:
    def test_list_models_not_found(self, client: TestClient, normal_user_token_headers):
        r = client.get(
            f"{settings.API_V1_STR}/models/batch",
            headers=normal_user_token_headers,
            params={"ids": "100,200,300"},
        )
        assert r.status_code == 200
        assert len(r.json()["result"]) == 0

    def test_list_models_given_ids(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers,
        mocker,
    ):
        model = create_model(db, user_id)
        r = client.get(
            f"{settings.API_V1_STR}/models/batch",
            headers=normal_user_token_headers,
            params={"ids": f"{model.id},200,300"},
        )
        assert len(r.json()["result"]) == 1


class TestDeleteModel:
    def test_delete_model(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        model = create_model(db, user_id)
        assert not model.is_deleted
        r = client.delete(
            f"{settings.API_V1_STR}/models/{model.id}",
            headers=normal_user_token_headers,
        )
        assert r.json()["result"]["is_deleted"]

    def test_delete_model_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.delete(f"{settings.API_V1_STR}/models/233333", headers=normal_user_token_headers)
        assert r.status_code == 404


class TestGetModel:
    def test_get_model(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        model = create_model(db, user_id)
        r = client.get(
            f"{settings.API_V1_STR}/models/{model.id}",
            headers=normal_user_token_headers,
        )
        assert model.hash == r.json()["result"]["hash"]

    def test_get_model_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.get(f"{settings.API_V1_STR}/models/233333", headers=normal_user_token_headers)
        assert r.status_code == 404


class TestImportModel:
    def test_import_model(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        project = create_project_record(db, user_id)
        model = create_model(db, user_id)
        j = {
            "project_id": project.id,
            "group_name": random_lower_string(),
            "input_model_id": model.id,
        }
        r = client.post(
            f"{settings.API_V1_STR}/models/importing",
            headers=normal_user_token_headers,
            json=j,
        )
        assert r.ok
        assert r.json()["result"]["group_name"] == j["group_name"]
