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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 40  # 40 hours
    APP_SECRET_KEY: str = secrets.token_urlsafe(32)
    DEFAULT_LIMIT: int = 20
    STRING_LEN_LIMIT: int = 100
    LONG_STRING_LEN_LIMIT: int = 500
    TEXT_LEN_LIMIT: int = 20000
    SENTRY_DSN: Optional[str]
    REGISTRATION_NEEDS_APPROVAL: bool = False

    FIRST_ADMIN: EmailStr = "admin@example.com"  # type: ignore
    FIRST_ADMIN_PASSWORD: str = "change_this"

    USE_200_EVERYWHERE: bool = True

    APP_API_TIMEOUT: int = 30
    APP_API_HOST: str = "backend:80"
    APP_API_KEY: str = secrets.token_urlsafe(32)

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

    INIT_LABEL_FOR_FIRST_USER: bool = True
    RETRY_INTERVAL_SECONDS: int = 15

    # migration
    MIGRATION_CHECKPOINT: str = "9bb7bb8b71c3"


settings = Settings(_env_file=".env")  # type: ignore
