import random
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.models.task import TaskType
from tests.utils.utils import random_lower_string
from app.api.api_v1.endpoints import models as m

def insert_model(db: Session, client: TestClient, token) -> models.Model:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=token)
    user_id = r.json()["result"]["id"]
    task_in = schemas.TaskCreate(
        name=random_lower_string(6),
        type=TaskType.training,
    )
    task = crud.task.create(db, obj_in=task_in)
    model_in = schemas.ModelCreate(
        hash=random_lower_string(10),
        name=random_lower_string(6),
        user_id=user_id,
        task_id=task.id,
    )
    model = crud.model.create(db, obj_in=model_in)
    return model


class TestListModels:
    def test_list_models_having_results(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        for _ in range(3):
            insert_model(db, client, normal_user_token_headers)
        r = client.get(
            f"{settings.API_V1_STR}/models/", headers=normal_user_token_headers
        )
        datasets = r.json()["result"]["items"]
        total = r.json()["result"]["total"]
        assert len(datasets) == total != 0

    def test_list_models_not_found(self, client: TestClient, normal_user_token_headers):
        r = client.get(
            f"{settings.API_V1_STR}/models/",
            headers=normal_user_token_headers,
            params={"ids": "100,200,300"},
        )
        assert r.status_code == 200
        assert len(r.json()["result"]["items"]) == 0

    def test_list_models_given_ids(
        self, db: Session, client: TestClient, normal_user_token_headers, mocker
    ):
        model = insert_model(db, client, normal_user_token_headers)
        r = client.get(
            f"{settings.API_V1_STR}/models/",
            headers=normal_user_token_headers,
            params={"ids": f"{model.id},200,300"},
        )
        datasets = r.json()["result"]["items"]
        total = r.json()["result"]["total"]
        assert total == 1


class TestChangeModelName:
    def test_change_model_name(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        model = insert_model(db, client, normal_user_token_headers)
        old_name = model.name
        new_name = random_lower_string(6)
        r = client.patch(
            f"{settings.API_V1_STR}/models/{model.id}",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.json()["result"]["name"] == new_name != old_name

    def test_change_model_name_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        new_name = random_lower_string(6)
        r = client.patch(
            f"{settings.API_V1_STR}/models/233333",
            headers=normal_user_token_headers,
            json={"name": new_name},
        )
        assert r.status_code == 404


class TestDeleteModel:
    def test_delete_model(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        model = insert_model(db, client, normal_user_token_headers)
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
        r = client.delete(
            f"{settings.API_V1_STR}/models/233333", headers=normal_user_token_headers
        )
        assert r.status_code == 404


class TestGetModel:
    def test_get_model(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        model = insert_model(db, client, normal_user_token_headers)
        r = client.get(
            f"{settings.API_V1_STR}/models/{model.id}",
            headers=normal_user_token_headers,
        )
        assert model.hash == r.json()["result"]["hash"]
        assert "config" in r.json()["result"]

    def test_get_model_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.get(
            f"{settings.API_V1_STR}/models/233333", headers=normal_user_token_headers
        )
        assert r.status_code == 404


class TestCreatePlaceholderTask:
    def test_create_placeholder_task(self, db, mocker):
        user_id = random.randint(1000, 2000)
        t = m.create_task_as_placeholder(db, user_id=user_id)
        assert t.user_id == user_id
        assert t.is_deleted == True
