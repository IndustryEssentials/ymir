import logging
from typing import Any, Dict, List

import redis
import yaml
from werkzeug.local import LocalProxy

from src.config import viz_settings


class RedisCache:
    def __init__(self, rds_client: redis.Redis):
        self._client = rds_client

    def get(self, key: str) -> Dict:
        try:
            raw_value = self._client.get(key)
        except Exception as e:
            logging.exception(f"{e}")
            return dict()
        if raw_value is None:
            return dict()
        content = yaml.safe_load(str(raw_value))

        return content

    def set(self, key: str, value: Any, timeout: int = None) -> None:
        if isinstance(value, dict):
            value = yaml.safe_dump(value)
        elif isinstance(value, str):
            value = value
        else:
            raise ValueError(f"Invalid redis value type: {type(value)}")
        self._client.set(key, value, timeout)

    def hmget(self, name: str, keys: List) -> List:
        return self._client.hmget(name, keys)

    def lrange(self, name: str, start: int, end: int) -> List:
        return self._client.lrange(name, start, end)

    def exists(self, names: str) -> int:
        try:
            return self._client.exists(names)
        except Exception as e:
            logging.exception(f"{e}")
            return False

    def pipeline(self) -> Any:
        return self._client.pipeline(transaction=False)

    def llen(self, name: str) -> int:
        return self._client.llen(name)

    def hget(self, name: str, key: str) -> Dict:
        res = self._client.hget(name, key)
        return yaml.safe_load(str(res))


def get_connect() -> redis.Redis:
    if viz_settings.REDIS_TESTING:
        import redislite
        redis_con = redislite.StrictRedis("/tmp/redis.db")
    else:
        redis_con = redis.StrictRedis.from_url(str(viz_settings.VIZ_REDIS_URI), encoding="utf8", decode_responses=True)
    return redis_con


proxy_rds_con = LocalProxy(get_connect)
redis_cache = RedisCache(proxy_rds_con)  # type: ignore
