from collections import defaultdict
from typing import List, Tuple, Dict

import arrow
from redis import StrictRedis
from arrow.arrow import Arrow
from app.config import settings

PRECISION = ["day", "week", "month"]


class RedisStats:
    def __init__(self, url: str, stats_group: List, tz: str = "Asia/Shanghai"):
        self.prefix = "stats"
        self.stats_group = stats_group
        self.conn = self._get_redis_con(url)
        self.tz = tz

    def _get_redis_con(self, redis_uri: str) -> StrictRedis:
        if settings.IS_TESTING:
            import redislite
            redis_con = redislite.StrictRedis('/tmp/redis.db')
        else:
            redis_con = StrictRedis.from_url(redis_uri)
        return redis_con

    def update_task_stats(self, user_id: int, task_type: int) -> None:
        """
        Calculate task counts by day, week, month,
        and group by task_type
        """
        key = f"{self.prefix}:{user_id}:task"
        assert task_type in self.stats_group
        self.update_counter(self.conn, key, str(task_type), tz=self.tz)

    def get_task_stats(
        self, user_id: int, precision: str, limit: int = 10
    ) -> defaultdict:
        key = f"{self.prefix}:{user_id}:task"

        # for every task_type, there is a List[(timestamp, count)]
        groupwise_stats = {
            group: dict(self.get_counter(self.conn, key, str(group), precision))
            for group in self.stats_group
        }

        # pivot stats by timestamp
        timewise_stats = defaultdict(dict)  # type: defaultdict
        now = arrow.now().to(self.tz).floor(precision)  # type: ignore
        for i in range(limit):
            t = now.shift(**{precision + "s": -i}).int_timestamp
            for group in self.stats_group:
                timewise_stats[t][group] = groupwise_stats[group].get(t, 0)
        return timewise_stats

    def update_model_rank(self, user_id: int, model_id: int) -> None:
        key = f"{self.prefix}:{user_id}:model"
        self._update_rank(self.conn, key, str(model_id))

    def update_keyword_wise_model_rank(self, user_id: int, model_id: int, model_mAP: float, keywords: List[str]) -> None:
        for keyword in keywords:
            key = f"{self.prefix}:{user_id}:model:{keyword}"
            self.conn.zadd(key, {str(model_id): model_mAP})

    def get_keyword_wise_best_models(self, user_id: int, limit: int = 5) -> Dict[str, List[Tuple[int, float]]]:
        """
        Get models of each keyword, sorted by mAP
        """
        prefix = f"{self.prefix}:{user_id}:model:"
        keyword_wise_models = {}
        for key in self.get_keys(self.conn, prefix):
            keyword = key.replace(prefix, "")
            keyword_wise_models[keyword] = [
                (int(model_id), mAP)
                for model_id, mAP in self._get_rank(self.conn, key, stop=limit)
            ]
        return keyword_wise_models

    def get_top_models(self, user_id: int, limit: int = 5) -> List[Tuple[int, int]]:
        key = f"{self.prefix}:{user_id}:model"
        return [
            (int(model_id), ref_count)
            for model_id, ref_count in self._get_rank(self.conn, key, stop=limit)
        ]

    def delete_model_rank(self, user_id: int, model_id: int) -> None:
        key = f"{self.prefix}:{user_id}:model"
        self._delete_rank(self.conn, key, str(model_id))

    def update_dataset_rank(self, user_id: int, dataset_id: int) -> None:
        key = f"{self.prefix}:{user_id}:dataset"
        self._update_rank(self.conn, key, str(dataset_id))

    def get_top_datasets(self, user_id: int, limit: int = 5) -> List:
        key = f"{self.prefix}:{user_id}:dataset"
        return [
            (int(dataset_id), ref_count)
            for dataset_id, ref_count in self._get_rank(self.conn, key, stop=limit)
        ]

    def delete_dataset_rank(self, user_id: int, dataset_id: int) -> None:
        key = f"{self.prefix}:{user_id}:dataset"
        self._delete_rank(self.conn, key, str(dataset_id))

    @staticmethod
    def _update_rank(
        conn: StrictRedis, key: str, name: str, count: int = 1
    ) -> None:
        # name, amount, value
        # "Increment the score of ``value`` in sorted set ``name`` by ``amount``"
        conn.zincrby(key, count, name)

    @staticmethod
    def _get_rank(
        conn: StrictRedis, key: str, start: int = 0, stop: int = -1
    ) -> List:
        return conn.zrange(key, start, stop, withscores=True, desc=True)

    @staticmethod
    def _delete_rank(conn: StrictRedis, key: str, name: str) -> None:
        conn.zrem(key, name)

    @staticmethod
    def update_counter(
        conn: StrictRedis,
        prefix: str,
        name: str,
        tz: str,
        count: int = 1,
        now: Arrow = None,
    ) -> None:
        now = now or arrow.now().to(tz)
        pipe = conn.pipeline()
        for prec in PRECISION:
            pnow = now.floor(prec).int_timestamp  # type: ignore
            hash = f"{prec}:{name}"
            pipe.zadd(f"{prefix}:known:", {hash: 0})
            pipe.hincrby(f"{prefix}:count:{hash}", str(pnow), count)
        pipe.execute()

    @staticmethod
    def get_counter(
        conn: StrictRedis, prefix: str, name: str, precision: str
    ) -> List:
        assert precision in PRECISION

        hash = f"{precision}:{name}"
        data = conn.hgetall(f"{prefix}:count:{hash}")
        counter = []
        for k, v in data.items():
            counter.append((int(k), int(v)))
        counter.sort()
        return counter

    @staticmethod
    def get_keys(
        conn: StrictRedis, prefix: str
    ) -> List:
        """
        Caution, use this func when you're sure there are limited keys
        """
        return list(conn.scan_iter(f"{prefix}*"))

    def close(self) -> None:
        print("bye")
