from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from tests.utils.tasks import create_task
from tests.utils.visualizations import create_visualization_record


class TestListVisualizations:
    def test_list_visualizations_with_results(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        task = create_task(db, user_id=user_id)
        create_visualization_record(db, task, user_id)
        r = client.get(f"{settings.API_V1_STR}/visualizations/", headers=normal_user_token_headers)
        items = r.json()["result"]["items"]
        assert len(items) != 0


class TestCreateVisualization:
    def test_create_visualization(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        task = create_task(db, user_id=user_id)
        j = {
            "task_ids": [task.id]
        }

        r = client.post(
            f"{settings.API_V1_STR}/visualizations/",
            headers=normal_user_token_headers,
            json=j,
        )
        assert r.ok
        assert r.json()["result"]["tid"] is not None
        assert r.json()["result"]["tasks"] is not None


class TestDeleteVisualization:
    def test_delete_visualization(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        task = create_task(db, user_id=user_id)
        visualization = create_visualization_record(db, task, user_id)
        assert not visualization.is_deleted
        r = client.delete(
            f"{settings.API_V1_STR}/visualizations/{visualization.id}",
            headers=normal_user_token_headers,
        )
        assert r.json()["result"]["is_deleted"]

    def test_delete_visualization_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        r = client.delete(f"{settings.API_V1_STR}/visualizations/233333", headers=normal_user_token_headers)
        assert r.status_code == 404
