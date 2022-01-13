import os
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir postman"
    API_HOST: str = os.environ['API_HOST']
    API_KEY_SECRET: str = os.environ['API_KEY_SECRET']
    BACKEND_CORS_ORIGINS: List[str] = []
    _RETRY_CACHE_KEY = 'retryhash:/events/taskstates'
    _IGNORE_FAILED_SECONDS = 3600 * 24 * 2  # two days
    _APP_RC_TASK_NOT_FOUND = 7001


settings = Settings()
