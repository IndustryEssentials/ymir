from typing import Dict

from fastapi.testclient import TestClient

from app.config import settings


class TestSysInfo:
    def test_get_users_normal_user_me(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ) -> None:
        r = client.get(f"{settings.API_V1_STR}/sys_info", headers=normal_user_token_headers)
        sys_info = r.json()["result"]
        assert sys_info["gpu_count"] == 233
