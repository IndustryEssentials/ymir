import pytest
from unittest.mock import MagicMock
from app.models import db


@pytest.mark.parametrize(
    "task,response_body",
    [
        (
            {
                "tid": "akbb23",
                "datas": [
                    {
                        "id": "32423xfcd33xxx",
                        "name": "ymir_data233",
                        "data_dir": "./ymir-workplace/voc",
                    }
                ],
            },
            {"code": 0, "data": {"tid": "akbb23"}, "error": None},
        ),
        (
            {
                "tid": "akbb23",
                "datas": [
                    {
                        "id": "32423xfcd33xxx",
                        "name": "ymir_data233",
                        "data_dir": "./ymir-workplace/voc",
                    }
                ],
            },
            {"code": 1002, "data": {}, "error": "task tid already exists"},
        ),
    ],
)
def test_task_create(test_app, task, response_body, monkeypatch):
    async def mock_get_task(payload):
        return response_body.get("code")

    monkeypatch.setattr(db, "get_task", mock_get_task)

    response = test_app.post(
        "/task/",
        json=task,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == response_body
