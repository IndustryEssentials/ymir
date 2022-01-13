import os
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir postman"
    API_HOST: str = os.environ['API_HOST']
    API_KEY_SECRET: str = os.environ['API_KEY_SECRET']
    PM_REDIS_URI: str = os.environ['PM_REDIS_URI']

    BACKEND_CORS_ORIGINS: List[str] = []

    RETRY_CACHE_KEY = 'retryhash:/events/taskstates'
    IGNORE_FAILED_SECONDS = 3600 * 24 * 2  # two days
    MAX_REDIS_STREAM_LENGTH = 10 * 3600 * 24 * 2  # two days, with 10 messages for each second


settings = Settings()
