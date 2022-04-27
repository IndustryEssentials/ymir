import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, EmailStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir app"
    FRONTEND_ENTRYPOINT: str = "localhost:8089"
    NGINX_PREFIX: str = ""
    API_V1_STR: str = "/api/v1"
    DATABASE_URI: str = "sqlite:///app.db"
    CLICKHOUSE_URI: str = "clickhouse"
    TOKEN_URL: str = "/auth/token"
    GRPC_CHANNEL: str = "controller:50066"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 40  # 40 hours
    APP_SECRET_KEY: str = secrets.token_urlsafe(32)
    DEFAULT_LIMIT: int = 20
    STRING_LEN_LIMIT: int = 100
    LONG_STRING_LEN_LIMIT: int = 500
    TEXT_LEN_LIMIT: int = 20000
    SENTRY_DSN: Optional[str]
    REGISTRATION_NEEDS_APPROVAL: bool = False

    # assets viz
    VIZ_HOST: str = "viz:9099"
    VIZ_TIMEOUT: int = 30

    FIRST_ADMIN: EmailStr = "admin@example.com"  # type: ignore
    FIRST_ADMIN_PASSWORD: str = "change_this"

    PUBLIC_DATASET_OWNER: int = 1

    USE_200_EVERYWHERE: bool = True

    REDIS_TESTING: bool = False
    APP_API_KEY: str = secrets.token_urlsafe(32)

    # paths to share data with Controller, etc
    SHARED_DATA_DIR: str = "./"
    MODELS_PATH: Optional[str] = None

    # redis
    BACKEND_REDIS_URL: str = "redis://redis:6379/0"

    # graph
    MAX_HOPS: int = 5

    # all the emails things
    EMAILS_ENABLED: bool = False
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "test@ymir.ai"  # type: ignore
    EMAILS_FROM_NAME: Optional[str] = "ymir-project"
    EMAIL_TEMPLATES_DIR: str = "/app/ymir_app/app/email-templates/build"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # RUNTIME
    RUNTIMES: Optional[
        str
    ] = '[{"name": "sample_image", "hash": "6d30c27861c5", "description": "Demonstration only. This docker image trains fake model after a requested length of running time period. These models can only be used by this same docker image for re-training/mining/inference purposes. Adjust the hyper-parameters to set the length of running time, or to trigger crash, to set expected mAP, etc", "url": "industryessentials/executor-example:latest", "configs": [{"expected_map": 0.983, "idle_seconds": 60, "trigger_crash": 0, "type": 1}, {"idle_seconds": 6, "trigger_crash": 0, "type": 2}, {"idle_seconds": 3, "trigger_crash": 0, "type": 9}]}]'  # noqa: E501

    # Online Sheet
    SHARING_TIMEOUT: int = 10
    WUFOO_URL: Optional[str]
    WUFOO_AUTHORIZATION: Optional[str]
    SHARED_DOCKER_IMAGES_URL: Optional[str]
    GITHUB_TIMEOUT: int = 30
    APP_CACHE_EXPIRE_IN_SECONDS: int = 3600

    # Start up stuffs
    # Task Type To Survive Upon Start up
    #  default TaskTypeLabel = 3
    TASK_TYPES_WHITELIST: List[int] = [3]
    INIT_LABEL_FOR_FIRST_USER: bool = True
    RETRY_INTERVAL_SECONDS: int = 15

    # Reverse keywords
    REVERSE_KEYWORDS_OUTPUT: bool = True

    # Sample Project configs
    SAMPLE_PROJECT_KEYWORDS: List[str] = ["person", "cat"]
    SAMPLE_PROJECT_TESTING_DATASET_URL: str = "http://web/val.zip"
    SAMPLE_PROJECT_MINING_DATASET_URL: str = "http://web/mining.zip"
    SAMPLE_PROJECT_MODEL_URL: str = "http://web/683f4fa14d1baa733a87d9644bb0457cbed5aba8"


settings = Settings(_env_file=".env")  # type: ignore
