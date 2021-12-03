from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from tests.utils.utils import random_lower_string


def test_create_workspace(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    data = {"name": random_lower_string(6), "hash": random_lower_string(6)}
    r = client.post(
        f"{settings.API_V1_STR}/workspaces/",
        headers=normal_user_token_headers,
        json=data,
    )
    current_workspace = r.json()["result"]
    assert current_workspace
    assert current_workspace["name"] == data["name"]
