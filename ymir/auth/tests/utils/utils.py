import random
import string
from typing import Dict

from fastapi.testclient import TestClient

from app.config import settings
from app.utils.security import frontend_hash


def random_lower_string(k: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))


def random_hash(hash_type: str = "asset") -> str:
    leading = hash_type[0]
    return leading + "0" * 9 + random_lower_string(40)


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_url() -> str:
    return f"https://www.{random_lower_string()}.com/{random_lower_string()}"


def get_admin_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_ADMIN,
        "password": frontend_hash(settings.FIRST_ADMIN_PASSWORD),
        "scope": "ADMIN",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    tokens = r.json()["result"]
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_super_admin_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_ADMIN,
        "password": frontend_hash(settings.FIRST_ADMIN_PASSWORD),
        "scope": "NORMAL ADMIN SUPER_ADMIN",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    tokens = r.json()["result"]
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
