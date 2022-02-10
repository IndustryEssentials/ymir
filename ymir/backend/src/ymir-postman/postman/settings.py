import os
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_API_HOST: str = os.environ['APP_API_HOST']
    APP_API_KEY: str = os.environ['APP_API_KEY']
    PM_REDIS_URI: str = os.environ['BACKEND_REDIS_URL']
    PM_URL: str = os.environ['POSTMAN_URL']

    BACKEND_CORS_ORIGINS: List[str] = []

    RETRY_CACHE_KEY = 'retryhash:/events/taskstates'
    MAX_REDIS_STREAM_LENGTH = 10 * 3600 * 24 * 2  # two days, with 10 messages for each second
    RETRY_SECONDS = 60


class Constants(BaseSettings):
    PROJECT_NAME: str = "ymir postman"
    EVENT_TOPIC_RAW = 'raw'
    EVENT_TOPIC_INNER = '_inner_'

    RC_OK = 0
    RC_FAILED_TO_UPDATE_TASK_STATUS = 110706


settings = Settings()
constants = Constants()
