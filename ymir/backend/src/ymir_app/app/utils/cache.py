import json
from typing import List, Optional, Union

from redis import StrictRedis

from app.config import settings

KEYWORDS_CACHE_KEY = "keywords"


class CacheClient:
    def __init__(self, redis_uri: str, user_id: int):
        self.prefix = "cache"
        self.user_id = user_id
        self.conn = self._get_redis_con(redis_uri)

    def config(self, user_id: int) -> None:
        self.user_id = user_id

    def _get_redis_con(self, redis_uri: str) -> StrictRedis:
        if settings.REDIS_TESTING:
            import redislite

            redis_con = redislite.StrictRedis("/tmp/redis.db")
        else:
            redis_con = StrictRedis.from_url(redis_uri)
        return redis_con

    def set(self, key: str, value: Union[str, dict]) -> None:
        redis_key = f"{self.prefix}:{self.user_id}:{key}"
        if isinstance(value, dict):
            value = json.dumps(value)
        self.conn.set(redis_key, value)

    def get(self, key: str) -> Optional[str]:
        redis_key = f"{self.prefix}:{self.user_id}:{key}"
        return self.conn.get(redis_key)

    def delete(self, key: str) -> None:
        redis_key = f"{self.prefix}:{self.user_id}:{key}"
        self.conn.delete(redis_key)

    def batch_delete(self, keys: List[str]) -> None:
        pipe = self.conn.pipeline()
        for key in keys:
            redis_key = f"{self.prefix}:{self.user_id}:{key}"
            pipe.delete(redis_key)
        pipe.execute()

    def delete_personal_keywords_cache(self) -> None:
        self.delete(KEYWORDS_CACHE_KEY)

    def close(self) -> None:
        self.conn.close()
