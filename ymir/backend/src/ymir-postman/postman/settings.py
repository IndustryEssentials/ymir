import os
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir postman"
    APP_API_HOST: str = os.environ['APP_API_HOST']
    APP_API_KEY: str = os.environ['APP_API_KEY']
    PM_REDIS_URI: str = os.environ['BACKEND_REDIS_URL']

    BACKEND_CORS_ORIGINS: List[str] = []

    RETRY_CACHE_KEY = 'retryhash:/events/taskstates'
    MAX_REDIS_STREAM_LENGTH = 10 * 3600 * 24 * 2  # two days, with 10 messages for each second

    EVENT_TOPIC_RAW = 'raw'
    EVENT_TOPIC_INNER = '_inner_'


settings = Settings()
