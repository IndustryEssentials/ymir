import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, EmailStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir auth"
    FRONTEND_ENTRYPOINT: str = "localhost:8089"
    NGINX_PREFIX: str = ""
    API_V1_STR: str = "/api/v1"
    DATABASE_URI: str = "sqlite:///auth.db"
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
    VIZ_TIMEOUT: int = 30

    FIRST_ADMIN: EmailStr = "admin@example.com"  # type: ignore
    FIRST_ADMIN_PASSWORD: str = "change_this"

    PUBLIC_DATASET_OWNER: int = 1

    USE_200_EVERYWHERE: bool = True

    REDIS_TESTING: bool = False
    APP_API_TIMEOUT: int = 30
    APP_API_HOST: str = "backend:80"
    APP_API_KEY: str = secrets.token_urlsafe(32)

    # paths to share data with Controller, etc
    SHARED_DATA_DIR: str = "./"
    MODELS_PATH: Optional[str] = None

    # redis
    BACKEND_REDIS_URL: str = "redis://redis:6379/0"

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
    EMAIL_TEMPLATES_DIR: str = "/app/ymir_auth/auth/email-templates/build"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # DOCKER IMAGE RUNTIMES
    DOCKER_IMAGES: Optional[
        str
    ] = '[{"name": "sample_image", "hash": "6d30c27861c5", "object_type": 2, "description": "Demonstration only. This docker image trains fake model after a requested length of running time period. These models can only be used by this same docker image for re-training/mining/inference purposes. Adjust the hyper-parameters to set the length of running time, or to trigger crash, to set expected mAP, etc", "url": "industryessentials/executor-example:latest", "configs": [{"expected_map": 0.983, "idle_seconds": 60, "trigger_crash": 0, "type": 1}, {"idle_seconds": 6, "trigger_crash": 0, "type": 2}, {"idle_seconds": 3, "trigger_crash": 0, "type": 9}]}]'  # noqa: E501

    # Start up stuffs
    # Task Type To Survive Upon Start up
    #  default TaskTypeLabel = 3
    TASK_TYPES_WHITELIST: List[int] = [3]
    INIT_LABEL_FOR_FIRST_USER: bool = True
    RETRY_INTERVAL_SECONDS: int = 15

    # ymir_viewer
    VIEWER_HOST_PORT: Optional[int] = None

    # migration
    MIGRATION_CHECKPOINT: str = "9bb7bb8b71c3"

    # cron job
    CRON_MIN_IDLE_TIME: int = 2 * 60 * 1000  # 2 minutes
    CRON_CHECK_INTERVAL: int = 10000  # 10 seconds
    CRON_UPDATE_TASK_BATCH_SIZE: int = 10
    CRON_UPDATE_TASK_RETRY_INTERVAL: int = 5

    YMIR_VERSION: str = "2.2.0"


settings = Settings(_env_file=".env")  # type: ignore
