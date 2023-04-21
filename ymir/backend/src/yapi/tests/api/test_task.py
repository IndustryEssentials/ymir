from typing import Dict

from fastapi.testclient import TestClient

from yapi.config import settings
from tests.utils.utils import gen_task_data
from yapi.api.api_v1.endpoints import tasks as m
from yapi.constants.state import ResultType


class TestListTasks:
    def test_list_tasks_with_result_dataset(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_task_data(i) for i in range(total)]}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(f"{settings.API_V1_STR}/tasks/", params={"limit": 100}, headers=normal_user_token_headers)
        result = r.json()["result"]
        assert len(result["items"]) == result["total"] == total
        for item in result["items"]:
            assert item["result"]["type"] == ResultType.dataset

    def test_list_tasks_with_result_model(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {
            "total": total,
            "items": [gen_task_data(i, {"result_model": {"id": i, "model_group_id": 1}}) for i in range(total)],
        }
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(f"{settings.API_V1_STR}/tasks/", params={"limit": 100}, headers=normal_user_token_headers)
        result = r.json()["result"]
        assert len(result["items"]) == result["total"] == total
        for item in result["items"]:
            assert item["result"]["type"] == ResultType.model

    def test_list_tasks_with_result_prediction(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": [gen_task_data(i, {"result_prediction": {"id": i}}) for i in range(total)]}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(f"{settings.API_V1_STR}/tasks/", params={"limit": 100}, headers=normal_user_token_headers)
        result = r.json()["result"]
        assert len(result["items"]) == result["total"] == total
        for item in result["items"]:
            assert item["result"]["type"] == ResultType.prediction

    def test_list_tasks_with_result_docker_image(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {
            "total": total,
            "items": [gen_task_data(i, {"result_docker_image": {"id": i}}) for i in range(total)],
        }
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(f"{settings.API_V1_STR}/tasks/", params={"limit": 100}, headers=normal_user_token_headers)
        result = r.json()["result"]
        assert len(result["items"]) == result["total"] == total
        for item in result["items"]:
            assert item["result"]["type"] == ResultType.docker_image


class TestGetTask:
    def test_get_task_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        task_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_task_data(task_id)}
        r = client.get(f"{settings.API_V1_STR}/tasks/233", headers=normal_user_token_headers)
        task = r.json()["result"]
        assert task["id"] == task_id


class TestTerminateTask:
    def test_terminate_task_successfully(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        mock_app.get.return_value.json.return_value = {"code": 0, "message": "ok"}
        r = client.post(
            f"{settings.API_V1_STR}/tasks/233/terminate",
            json={"fetch_result": False},
            headers=normal_user_token_headers,
        )
        called_url = mock_app.post.call_args[0][0]
        assert called_url.endswith("terminate")
        result = r.json()
        assert result["code"] == 0


class TestTrainTask:
    def test_train_task_successfully(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        mocker.patch.object(m, "must_get_model_stage_id", return_value=1)
        task_id = 23
        payload = {
            "project_id": 2,
            "class_names": ["person", "cat"],
            "dataset_version_id": 1,
            "docker_image_config": {},
            "docker_image_id": 1,
            "model_version_id": 1,
            "validation_dataset_version_id": 1,
        }

        mock_app.post.return_value.json.return_value = {"code": 0, "result": {"id": task_id}}
        r = client.post(
            f"{settings.API_V1_STR}/tasks/train",
            json=payload,
            headers=normal_user_token_headers,
        )
        result = r.json()
        assert result["code"] == 0
        assert result["result"] == task_id


class TestMiningTask:
    def test_mining_task_successfully(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        mocker.patch.object(m, "must_get_model_stage_id", return_value=1)
        task_id = 23
        payload = {
            "project_id": 2,
            "class_names": ["person", "cat"],
            "dataset_version_id": 1,
            "docker_image_config": {},
            "docker_image_id": 1,
            "model_version_id": 1,
            "validation_dataset_version_id": 1,
            "top_k": 233,
        }

        mock_app.post.return_value.json.return_value = {"code": 0, "result": {"id": task_id}}
        r = client.post(
            f"{settings.API_V1_STR}/tasks/mine",
            json=payload,
            headers=normal_user_token_headers,
        )
        result = r.json()
        assert result["code"] == 0
        assert result["result"] == task_id


class TestInferenceTask:
    def test_inference_task_successfully(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        mocker.patch.object(m, "must_get_model_stage_id", return_value=1)
        task_id = 23
        payload = {
            "project_id": 2,
            "class_names": ["person", "cat"],
            "dataset_version_id": 1,
            "docker_image_config": {},
            "docker_image_id": 1,
            "model_version_id": 1,
            "validation_dataset_version_id": 1,
        }

        mock_app.post.return_value.json.return_value = {"code": 0, "result": {"id": task_id}}
        r = client.post(
            f"{settings.API_V1_STR}/tasks/inference",
            json=payload,
            headers=normal_user_token_headers,
        )
        result = r.json()
        assert result["code"] == 0
        assert result["result"] == task_id
