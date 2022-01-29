from fastapi.testclient import TestClient
from unittest import mock

class TestReg:
    def test_reg(self, client: TestClient):
        body = dict(
            task_id="abcdadf",
            user_id="12",
            log_paths=["/home/chao/lif_code/test/monitor.txt", "/home/chao/lif_code/test/m2.txt"],
        )

        r = client.post(f"/api/v1/tasks", json=body)

        print(r.content)
        #
        # assert r.ok
        # result = r.json()["result"]
        # assert result["total"] == len(result["items"])
        # assert "is_shared" in result["items"][0]