import requests
from fastapi.logger import logger

from auth.config import settings
from auth.api.errors.errors import FailedToCreateUser


def register_sandbox(user_id: int) -> None:
    url = f"http://{settings.APP_API_HOST}{settings.API_V1_STR}/users/controller"
    resp = requests.post(
        url, json={"user_id": user_id}, timeout=settings.APP_API_TIMEOUT, headers={"api-key": settings.APP_API_KEY}
    )
    if not resp.ok:
        logger.error("Failed to create sandbox via APP: %s", resp.content)
        raise FailedToCreateUser()
