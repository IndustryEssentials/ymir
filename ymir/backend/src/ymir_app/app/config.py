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
    ] = '[{"name": "default_training_image", "hash": "78aedb55de93", "type": 1, "url": "industryessentials/executor-det-yolov4-training:release-0.5.0", "config": "{\\"anchors\\": \\"12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401\\", \\"image_height\\": 608, \\"image_width\\": 608, \\"learning_rate\\": 0.0013, \\"max_batches\\": 20000, \\"warmup_iterations\\": 1000, \\"batch\\": 64, \\"subdivisions\\": 32, \\"shm_size\\": \\"16G\\"}"}, {"name": "default_mining_image", "hash": "33d61932b98f", "type": 2, "url": "industryessentials/executor-det-yolov4-mining:release-0.5.0", "config": "{\\"data_workers\\": 28, \\"model_name\\": \\"yolo\\", \\"model_type\\": \\"detection\\", \\"strategy\\": \\"aldd_yolo\\", \\"image_height\\": 608, \\"image_width\\": 608, \\"batch_size\\": 16, \\"anchors\\": \\"12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401\\", \\"confidence_thresh\\": 0.1, \\"nms_thresh\\": 0.45, \\"max_boxes\\": 50}"}, {"name": "default_inference_image", "hash": "33d61932b98f", "type": 9, "url": "industryessentials/executor-det-yolov4-mining:release-0.5.0", "config": "{\\"image_height\\": 608, \\"image_width\\": 608, \\"anchors\\": \\"12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401\\", \\"write_result\\": true, \\"confidence_thresh\\": 0.1, \\"nms_thresh\\": 0.45, \\"max_boxes\\": 50}"}]'  # noqa: E501

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


settings = Settings(_env_file=".env")  # type: ignore
