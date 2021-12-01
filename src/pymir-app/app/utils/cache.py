import json
from typing import Dict, Generator, List, Optional, Tuple, Union

from redis import StrictRedis
from app.config import settings


CACHED_KEYS = [KEYWORDS_CACHE_KEY, KEYWORD_ID_TO_NAME_KEY, KEYWORD_NAME_TO_ID_KEY] = [
    "keywords",
    "keyword_id_name",
    "keyword_name_id",
]


class CacheClient:
    def __init__(self, redis_uri: str, user_id: int):
        self.prefix = "cache"
        self.user_id = user_id
        self.conn = self._get_redis_con(redis_uri)

    def config(self, user_id: int) -> None:
        self.user_id = user_id

    def _get_redis_con(self, redis_uri: str) -> StrictRedis:
        if settings.IS_TESTING:
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
            pipe.delete(key)
        pipe.execute()

    def delete_personal_keywords(self) -> None:
        self.batch_delete(CACHED_KEYS)

    def close(self) -> None:
        self.conn.close()
