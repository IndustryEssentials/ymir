import json
from typing import Dict, Any, List, Optional

import redis
from werkzeug.local import LocalProxy

from src import config
from src.libs import app_logger


class RedisCache:
    def __init__(self, rds_client: redis.Redis):
        self._client = rds_client

    def get(self, key: str) -> Dict:
        raw_value = self._client.get(key)
        if raw_value is None:
            return dict()
        try:
            content = json.loads(str(raw_value))
        except ValueError as e:
            app_logger.logger.warning(f"loads {raw_value} error: {e}")
            content = dict()

        return content

    def set(self, key: str, value: Any, timeout: int = None) -> None:
        if isinstance(value, dict):
            value = json.dumps(value)
        self._client.set(key, value, timeout)

    def hmget(self, name: str, keys: List) -> List:
        return self._client.hmget(name, keys)

    def lrange(self, name: str, start: int, end: int) -> List:
        return self._client.lrange(name, start, end)

    def exists(self, names: str) -> int:
        try:
            return self._client.exists(names)
        except Exception as e:
            app_logger.logger.error(f"{e}")
            return False

    def pipeline(self) -> Any:
        return self._client.pipeline(transaction=False)

    def llen(self, name: str) -> int:
        return self._client.llen(name)

    def hget(self, name: str, key: str) -> Optional[Dict]:
        try:
            res = self._client.hget(name, key)
            return json.loads(str(res))
        except Exception as e:
            app_logger.logger.error(f"{e}")
            return None


def get_connect() -> redis.Redis:
    return redis.StrictRedis.from_url(str(config.VIZ_REDIS_URI), encoding="utf8", decode_responses=True)


proxy_rds_con = LocalProxy(get_connect)
redis_cache = RedisCache(proxy_rds_con)  # type: ignore
