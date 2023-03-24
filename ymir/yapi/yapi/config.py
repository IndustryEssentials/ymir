from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir yapi"
    API_V1_STR: str = "/api/v1"

    DEFAULT_LIMIT: int = 20

    SENTRY_DSN: Optional[str]

    APP_URL_PREFIX: str = "http://backend:80/api/v1"
    APP_TIMEOUT: int = 30

    USE_200_EVERYWHERE: bool = False

    # redis
    BACKEND_REDIS_URL: str = "redis://redis:6379/0"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []


settings = Settings(_env_file=".env")  # type: ignore
