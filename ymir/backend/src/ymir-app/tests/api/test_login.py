from fastapi.testclient import TestClient

from app.api.api_v1.endpoints import login as m
from app.api.errors.errors import InvalidToken
from app.config import settings
from app.utils.security import frontend_hash
from tests.utils.utils import random_email, random_lower_string


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_ADMIN,
        "password": frontend_hash(settings.FIRST_ADMIN_PASSWORD),
    }
    r = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


class TestRecoverPassword:
    def test_recover_password_user_not_found(self, client: TestClient):
        email = random_email()
        r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")
        assert r.status_code == 404

    def test_recover_password(self, client: TestClient, mocker):
        email = random_email()
        mock_crud = mocker.Mock()
        mocker.patch.object(m, "crud", return_value=mock_crud)

        mock_user = mocker.Mock(email=email)
        mock_crud.user.get_by_email.return_value = mock_user
        mocker.patch.object(m, "send_reset_password_email")

        r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")
        assert r.status_code == 200


class TestResetPassword:
    def test_reset_password_not_found(self, client: TestClient):
        j = {
            "token": random_lower_string(),
            "new_password": random_lower_string(),
        }
        r = client.post(f"{settings.API_V1_STR}/reset-password/", json=j)
        assert r.status_code == 401
        assert r.json()["code"] == InvalidToken.code
