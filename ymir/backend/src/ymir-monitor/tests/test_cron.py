import requests
from fastapi.testclient import TestClient

from monitor.utils.crontab_job import monitor_percent_log


def test_monitor_percent_log(client: TestClient, clear_redislite, mocker):
    mocker.patch("os.path.exists", return_value=True)
    data = "task_id_1	21245543	0.50	2"
    mocker.patch("builtins.open", mocker.mock_open(read_data=data))
    body = dict(task_id="task_id_1", user_id="12", log_paths=["/data/test/monitor.txt"],)
    client.post(f"/api/v1/tasks", json=body)

    data = "task_id_1	21245567	1	3"
    mocker.patch("builtins.open", mocker.mock_open(read_data=data))

    mock_resp = mocker.Mock()
    mock_resp.raise_for_status = mocker.Mock()
    mock_resp.status_code = 200
    mocker.patch.object(requests, "post", return_value=mock_resp)

    monitor_percent_log()

    r = client.get(f"/api/v1/finished_tasks")

    running_content = {
        "result": {
            "task_id_1": {
                "raw_log_contents": {
                    "/data/test/monitor.txt": {
                        "task_id": "task_id_1",
                        "timestamp": "21245567",
                        "percent": 1.0,
                        "state": 3,
                        "state_code": 0,
                        "state_message": None,
                        "stack_error_info": None,
                    }
                },
                "task_extra_info": {
                    "user_id": "12",
                    "monitor_type": 1,
                    "log_paths": ["/data/test/monitor.txt"],
                    "description": None,
                },
                "percent_result": {
                    "task_id": "task_id_1",
                    "timestamp": "21245567",
                    "percent": 1.0,
                    "state": 3,
                    "state_code": 0,
                    "state_message": None,
                    "stack_error_info": None,
                },
            }
        }
    }

    assert r.json() == running_content
