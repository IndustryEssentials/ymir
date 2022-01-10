from redis import StrictRedis, Redis
import json
from source.config import settings


def init_redis_pool(redis_uri: str = settings.MONITOR_REDIS_URI):
    return StrictRedis.from_url(redis_uri, encoding="utf8", decode_responses=True)


class RedisHandler:
    def __init__(self, redis: Redis = init_redis_pool()) -> None:
        self._redis = redis

    def set(self, name, key):
        self._redis.set(name, key)

    def get(self, name):
        return self._redis.get(name)

    def hset(self, name, key, value):
        self._redis.hset(name=name, key=key, value=json.dumps(value))

    def hdel(self, name, *keys):
        self._redis.hdel(name, *keys)

    def hexists(self, name, key) -> bool:
        return self._redis.hexists(name, key)

    def hmset(self, name, mapping):
        self._redis.hset(name=name, mapping={key: json.dumps(value) for key, value in mapping.items()})

    def hgetall(self, name):
        return {item: json.loads(value) for item, value in self._redis.hgetall(name=name).items()}
