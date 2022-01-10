import secrets
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir monitor"
    FRONTEND_ENTRYPOINT: str = "localhost:8089"
    NGINX_PREFIX: str = ""
    API_V1_STR: str = "/api/v1"
    INTERVAL_SECONDS: int = 60
    MONITOR_SENTRY_DSN: str = None

    MONITOR_RUNNING_KEY: str = "MONITOR_RUNNING_KEY:v1"
    MONITOR_FINISHED_KEY: str = "MONITOR_FINISHED_KEY:v1"

    DESTINATION_URL: str = ""
    MONITOR_REDIS_URI: str = "redis://localhost"


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")  # type: ignore
