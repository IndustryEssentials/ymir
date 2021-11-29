import secrets
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir app"
    FRONTEND_ENTRYPOINT: str = "localhost:8089"
    NGINX_PREFIX: str = ""
    API_V1_STR: str = "/api/v1"
    DATABASE_URI: str = "sqlite:///app.db"
    TOKEN_URL: str = "/auth/token"
    GRPC_CHANNEL: str = "controller:50066"
    DEFAULT_LIMIT: int = 20
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # Eight days
    SECRET_KEY: str = secrets.token_urlsafe(32)
    HASH_LEN_LIMIT: int = 50
    NAME_LEN_LIMIT: int = 100
    PARA_LEN_LIMIT: int = 500
    PRED_LEN_LIMIT: int = 20000
    SENTRY_DSN: Optional[str]

    # assets viz
    VIZ_HOST: str = "viz:9099"
    VIZ_TIMEOUT: int = 10

    FIRST_ADMIN: EmailStr = "admin@example.com"  # type: ignore
    FIRST_ADMIN_PASSWORD: str = "change_this"

    PUBLIC_DATASET_OWNER: int = 1

    USE_200_EVERYWHERE: bool = True

    IS_TESTING: bool = False

    # paths to share data with Controller, etc
    SHARED_DATA_DIR: str = "./"
    MODELS_PATH: Optional[str] = None

    # redis
    REDIS_URI: str = "redis://redis:6379/0"

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
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "ymir-notice@intellif.com"  # type: ignore
    EMAILS_FROM_NAME: Optional[str] = "ymir-project"
    EMAIL_TEMPLATES_DIR: str = "/app/pymir-app/app/email-templates/build"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # RUNTIME
    RUNTIMES: Optional[
        str
    ] = '[{"name": "default_training_image", "hash": "c142fa8de527", "type": 1, "config": "{\\"anchors\\": \\"12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401\\", \\"image_height\\": 608, \\"image_width\\": 608, \\"learning_rate\\": 0.0013, \\"max_batches\\": 20000, \\"warmup_iterations\\": 1000, \\"pretrained_model_params\\": \\"/fake_model\\", \\"batch\\": 64, \\"subdivisions\\": 32, \\"shm_size\\": \\"16G\\"}"}, {"name": "default_mining_image", "hash": "36b26c2071cf", "type": 2, "config": "{\\"data_workers\\": 28, \\"model_name\\": \\"yolo\\", \\"model_type\\": \\"detection\\", \\"strategy\\": \\"aldd_yolo\\", \\"image_height\\": 608, \\"image_width\\": 608, \\"batch_size\\": 16}"}, {"name": "default_inference_image", "hash": "36b26c2071cf", "type": 100, "config": "{\\"image_height\\": 608, \\"image_width\\": 608, \\"anchors\\": \\"12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401\\", \\"write_result\\": true, \\"confidence_thresh\\": 0.1, \\"nms_thresh\\": 0.45, \\"max_boxes\\": 50}"}]'


settings = Settings(_env_file=".env")  # type: ignore
