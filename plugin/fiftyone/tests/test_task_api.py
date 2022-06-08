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
                        "data_type": 0,
                        "data_dir": "./tests/test_data/voc",
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
                        "data_type": 0,
                        "data_dir": "./tests/test_data/voc",
                    }
                ],
            },
            {"code": 1010, "data": None, "error": "tid is required"},
        ),
        (
            {
                "tid": "akbb23",
                "datas": [
                    {
                        "id": "32423xfcd33xxx",
                        "name": "ymir_data233",
                        "data_type": 0,
                        "data_dir": "./tests/test_data/voc",
                    },
                    {
                        "id": "32423xfcd33xxx2",
                        "name": "ymir_data233",
                        "data_type": 0,
                        "data_dir": "./tests/test_data/voc",
                    },
                ],
            },
            {"code": 1010, "data": None, "error": None},
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


@pytest.mark.parametrize(
    "tid,response_body",
    [
        (
            "akbb23",
            {"code": 0, "data": {"status": "ready", "url": "http://127.0.0.1:8888/fiftyone/datasets/akbb23"}, "error": None}
        ),
        (
            "akbb25",
            {"code": 0, "data": {"status": "pending"}, "error": None}
        )
    ]
)
def test_task_query(test_app, tid, response_body, monkeypatch):
    async def mock_query_task(tid: str):
        return {"code": 0, "data": {"status": "ready", "url": "http://127.0.0.1:8888/fiftyone/datasets/akbb23"}, "error": None}

    monkeypatch.setattr(task_routes, "task_query", mock_query_task)

    response = test_app.get(
        f"/task/{tid}",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.json().get("code") == response_body.get("code")


@pytest.mark.parametrize(
    "tid,response_body",
    [
        (
            "akbb23",
            {"code": 0, "data": None, "error": None}
        ),
    ]
)
def test_task_delete(test_app, tid, response_body, monkeypatch):
    async def mock_delete_task(tid: str):
        return {"code": 0, "data": None, "error": None}

    monkeypatch.setattr(task_routes, "task_delete", mock_delete_task)

    response = test_app.delete(
        f"/task/{tid}",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.json().get("code") == response_body.get("code")