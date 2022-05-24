from typing import List

from environs import Env

env = Env()


class Config:
    mongo_uri: str = env.str("MONGO_URI", "mongodb://localhost:27017/")
    redis_host: str = env.str("REDIS_HOST", "localhost")
    redis_port: int = env.int("REDIS_PORT", 6379)
    redis_db: int = env.int("REDIS_DB", 0)
    allowed_hosts: List[str] = ["*"]


conf = Config()
