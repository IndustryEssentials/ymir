from typing import List

from environs import Env

env = Env()


class Config:
    debug: bool = env.bool("FIFTYONE_DEBUG", False)
    mongo_uri: str = env.str("FIFTYONE_DATABASE_URI", "mongodb://localhost:27017")
    fiftyone_database_name = env.str("FIFTYONE_DATABASE_NAME", "fiftyone")
    redis_host: str = env.str("FIFTYONE_REDIS_HOST", "localhost")
    redis_port: int = env.int("FIFTYONE_REDIS_PORT", 6379)
    redis_db: int = env.int("FIFTYONE_REDIS_DB", 0)
    # YOUR PROJECT PATH
    base_path: str = env.str(
        "FIFTYONE_BASE_PATH",
        "",
    )
    allowed_hosts: List[str] = ["*"]


conf = Config()
