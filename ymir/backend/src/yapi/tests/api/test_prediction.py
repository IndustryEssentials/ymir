from typing import Dict

from fastapi.testclient import TestClient

from yapi.config import settings
from tests.utils.utils import gen_prediction_data


class TestListPredictions:
    def test_list_predictions_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        total = 5
        app_resp = {"total": total, "items": {i: [gen_prediction_data(i)] for i in range(total)}}
        mock_app.get.return_value.json.return_value = {"code": 0, "result": app_resp}
        r = client.get(
            f"{settings.API_V1_STR}/predictions/", params={"project_id": 100}, headers=normal_user_token_headers
        )
        assert len(r.json()["result"]["items"]) == r.json()["result"]["total"] == total


class TestGetPrediction:
    def test_get_prediction_succeed(
        self,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
        mock_app,
    ):
        prediction_id = 233
        mock_app.get.return_value.json.return_value = {"code": 0, "result": gen_prediction_data(prediction_id)}
        r = client.get(f"{settings.API_V1_STR}/predictions/{prediction_id}", headers=normal_user_token_headers)
        prediction = r.json()["result"]
        assert prediction["id"] == prediction_id
