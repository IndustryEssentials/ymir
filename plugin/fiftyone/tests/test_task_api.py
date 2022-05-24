import pytest

from app.routes import task as task_routes


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
                "datas": [
                    {
                        "id": "32423xfcd33xxx",
                        "name": "ymir_data233",
                        "data_dir": "./ymir-workplace/voc",
                    }
                ],
            },
            {"code": 1006, "data": None, "error": "tid is required"},
        ),
    ],
)
def test_task_create(test_app, task, response_body, monkeypatch):
    async def mock_get_task(payload):
        return {"code": 0, "data": {"tid": payload.tid}, "error": None}

    monkeypatch.setattr(task_routes, "task_create", mock_get_task)

    response = test_app.post(
        "/task/",
        json=task,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.json().get("code") == response_body.get("code")
