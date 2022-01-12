from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ymir monitor"
    INTERVAL_SECONDS: int = 60
    MONITOR_SENTRY_DSN: str = ""

    MONITOR_RUNNING_KEY: str = "MONITOR_RUNNING_KEY:v1"
    MONITOR_FINISHED_KEY: str = "MONITOR_FINISHED_KEY:v1"

    ED_URL: str = ""
    MONITOR_REDIS_URI: str = "redis://localhost"


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")  # type: ignore
