from typing import Dict, List, Optional

import redis
import json
from controller.utils.app_logger import logger

from controller.config import REDIS_URI


class MiddlewareRedis:
    def __init__(self, rds_client: redis.Redis):
        self._client = rds_client

    def hmset(self, name: str, mapping: Dict) -> bool:
        return self._client.hmset(name, mapping)

    def hget(self, name: str, key: str) -> Optional[Dict]:
        try:
            res = self._client.hget(name, key)
            return json.loads(str(res))
        except json.JSONDecodeError as e:
            logger.error(f"{e}")
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
    return redis.StrictRedis.from_url(REDIS_URI, encoding="utf8", decode_responses=True)


rds = MiddlewareRedis(get_redis_connect())
