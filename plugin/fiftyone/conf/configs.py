from typing import List

from environs import Env

env = Env()


class Config:
    mongo_uri: str = env.str("FIFTYONE_DATABASE_URI", "mongodb://localhost:27017/")
    redis_host: str = env.str("FIFTYONE_REDIS_HOST", "localhost")
    redis_port: int = env.int("FIFTYONE_REDIS_PORT", 6379)
    redis_db: int = env.int("FIFTYONE_REDIS_DB", 0)
    allowed_hosts: List[str] = ["*"]


conf = Config()
