import secrets
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir monitor"
    FRONTEND_ENTRYPOINT: str = "localhost:8089"
    NGINX_PREFIX: str = ""
    API_V1_STR: str = "/api/v1"
    DEFAULT_LIMIT: int = 20
    MONITOR_SENTRY_DSN: str = None

    MONITOR_RUNNING_KEY = "MONITOR_RUNNING_KEY:v1"
    MONITOR_FINISHED_KEY = "MONITOR_FINISHED_KEY:v1"

    DESTINATION_URL = ""


settings = Settings(_env_file=".env", _env_file_encoding='utf-8')  # type: ignore
