import json
from typing import Dict

from redis import StrictRedis, Redis

from monitor.config import settings


def init_redis_pool(redis_uri: str = settings.BACKEND_REDIS_URL) -> Redis:
    if settings.REDIS_TESTING:
        import redislite

        redis_con = redislite.StrictRedis("/tmp/redis.db", encoding="utf8", decode_responses=True)
    else:
        redis_con = StrictRedis.from_url(redis_uri, encoding="utf8", decode_responses=True)

    return redis_con


class RedisHandler:
    def __init__(self, redis: Redis = init_redis_pool()) -> None:
        self._redis = redis

    def set(self, name: str, key: str) -> None:
        self._redis.set(name, key)

    def get(self, name: str) -> str:
        return self._redis.get(name)  # type: ignore

    def xadd(self, name: str, fields: Dict) -> None:
        self._redis.xadd(name, fields)

    def hset(self, name: str, key: str, value: Dict) -> None:
        self._redis.hset(name=name, key=key, value=json.dumps(value))

    def hdel(self, name: str, *keys: str) -> None:
        self._redis.hdel(name, *keys)

    def hexists(self, name: str, key: str) -> bool:
        return self._redis.hexists(name, key)

    def hmset(self, name: str, mapping: Dict) -> None:
        self._redis.hset(name=name, mapping={key: json.dumps(value) for key, value in mapping.items()})

    def hgetall(self, name: str) -> Dict:
        return {item: json.loads(value) for item, value in self._redis.hgetall(name=name).items()}
