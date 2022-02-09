import json
import logging
from typing import Dict, List, Optional

import redis

from controller.config import common_task as common_task_config


class MiddlewareRedis:
    def __init__(self, rds_client: redis.Redis):
        self._client = rds_client

    def hset(self, name: str, mapping: Dict) -> int:
        return self._client.hset(name=name, mapping=mapping)

    def hget(self, name: str, key: str) -> Optional[Dict]:
        try:
            res = self._client.hget(name, key)
            return json.loads(str(res))
        except json.JSONDecodeError as e:
            logging.error(f"{e}")
            return None

    def hgetall(self, name: str) -> Dict:
        return self._client.hgetall(name)

    def hdel(self, name: str, keys: str) -> int:
        return self._client.hdel(name, keys)

    def zadd(self, name: str, mapping: Dict) -> None:
        self._client.zadd(name, mapping)

    def zremrangebyscore(self, name: str, max: float, min: float = 1635403757) -> None:
        self._client.zremrangebyscore(name, min, max)

    def zrange(self, name: str, start: int = 0, end: int = -1) -> List:
        return self._client.zrange(name, start, end)


def get_redis_connect() -> redis.Redis:
    return redis.StrictRedis.from_url(common_task_config.BACKEND_REDIS_URL, encoding="utf8", decode_responses=True)


rds = MiddlewareRedis(get_redis_connect())
