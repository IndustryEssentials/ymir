import requests
from fastapi.testclient import TestClient

from monitor.utils.crontab_job import monitor_task_logs


def test_monitor_percent_log(client: TestClient, clear_redislite, mocker, tmp_path):
    log_path = tmp_path / "monitor.txt"
    log_path.write_text("task_id_1	21245543	0.50	2")

    body = {
        "task_id": "task_id_1",
        "user_id": "12",
        "log_path_weights": {str(log_path): 1.0},
    }
    client.post("/api/v1/tasks", json=body)

    log_path.write_text("task_id_1	21245567	1	3")

    mock_resp = mocker.Mock()
    mock_resp.raise_for_status = mocker.Mock()
    mock_resp.status_code = 200
    mocker.patch.object(requests, "post", return_value=mock_resp)

    monitor_task_logs()

    r = client.get("/api/v1/finished_tasks")

    running_content = {
        "result": {
            "task_id_1": {
                "raw_log_contents": {
                    str(log_path): {
                        "task_id": "task_id_1",
                        "timestamp": "21245567.0",
                        "percent": 1.0,
                        "state": 3,
                        "state_code": 0,
                        "state_message": None,
                        "stack_error_info": None,
                    }
                },
                "task_extra_info": {
                    "monitor_type": 1,
                    "log_path_weights": {str(log_path): 1.0},
                    "description": None,
                },
                "percent_result": {
                    "task_id": "task_id_1",
                    "timestamp": "21245567.0",
                    "percent": 1.0,
                    "state": 3,
                    "state_code": 0,
                    "state_message": None,
                    "stack_error_info": None,
                },
            }
        }
    }

    assert r.json()["result"]["task_id_1"] == running_content["result"]["task_id_1"]
