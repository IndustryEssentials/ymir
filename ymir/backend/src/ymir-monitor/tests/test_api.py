from fastapi.testclient import TestClient


class TestReg:
    def test_reg(self, client: TestClient, clear_redislite, mocker):
        mocker.patch("os.path.exists", return_value=True)

        data = "t0000003000003df78d31639637101	21245543	0.50	2"
        mocker.patch("builtins.open", mocker.mock_open(read_data=data))

        body = dict(
            task_id="abcdadf",
            user_id="12",
            log_path_weights={
                "/data/test/monitor.txtaa": 0.5,
                "/data/test/m2.txtaa": 0.5
            },
        )
        r = client.post("/api/v1/tasks", json=body)
        assert r.status_code == 200

        r = client.post("/api/v1/tasks", json=body)
        assert r.status_code == 400
