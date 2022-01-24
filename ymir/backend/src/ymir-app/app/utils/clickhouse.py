from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from clickhouse_driver import Client
from fastapi.logger import logger

from app.api.errors.errors import FailedToConnectClickHouse
from app.constants.state import TaskType
from app.utils.data import groupby


@dataclass
class ModelwithmAP:
    user_id: int
    model_id: int
    keyword: str
    mAP: float
    rank: int

    @classmethod
    def from_clickhouse(cls, res: Tuple) -> "ModelwithmAP":
        return cls(*res)


@dataclass
class TaskCount:
    type_: str
    count: int
    time: datetime

    @classmethod
    def from_clickhouse(cls, res: Tuple) -> "TaskCount":
        return cls(*res)


class YmirClickHouse:
    def __init__(self, host: str):
        self.client = Client(host=host)

    def execute(self, query: str, params: Optional[Any] = None) -> Any:
        try:
            records = self.client.execute(query, params)
        except Exception:
            raise FailedToConnectClickHouse()
        return records

    def save_task_parameter(
        self,
        dt: datetime,
        user_id: int,
        name: str,
        hash_: str,
        type_: str,
        dataset_ids: List[int],
        model_ids: List[int],
        keywords: List[str],
    ) -> Any:
        return self.execute(
            "INSERT INTO task_create VALUES",
            [[dt, user_id, name, hash_, type_, dataset_ids, model_ids, keywords]],
        )

    def save_model_result(
        self,
        dt: datetime,
        user_id: int,
        id_: int,
        name: str,
        hash_: str,
        map_: float,
        keywords: List[str],
    ) -> Any:
        return self.execute(
            "INSERT INTO model VALUES",
            [[dt, user_id, id_, name, hash_, map_, keywords]],
        )

    def save_dataset_keyword(
        self, dt: datetime, user_id: int, dataset_id: int, keywords: List[str]
    ) -> Any:
        return self.execute(
            "INSERT INTO dataset_keywords VALUES", [[dt, user_id, dataset_id, keywords]]
        )

    def get_popular_items(self, user_id: int, column: str, limit: int = 10) -> Any:
        """
        Get most popular datasets, models or keywords
        """
        sql = f"""\
SELECT
    {column} AS item,
    count({column}) AS ref_count
FROM task_create
ARRAY JOIN {column}
WHERE user_id = %(user_id)s
GROUP BY {column}
ORDER BY ref_count DESC
LIMIT %(limit)s"""
        return self.execute(sql, {"user_id": user_id, "limit": limit})

    def get_models_order_by_map(
        self, user_id: int, keywords: Optional[List[str]] = None, limit: int = 10
    ) -> Any:
        """
        Get models of highest mAP score, partitioned by keywords
        """
        sql = """\
SELECT
    user_id,
    id,
    keyword_ids,
    map,
    RANK() OVER (PARTITION BY user_id, keyword_ids ORDER BY map DESC) AS ranking
FROM
(
    SELECT
        user_id,
        id,
        keyword_ids,
        map
    FROM model
    ARRAY JOIN keyword_ids
    WHERE user_id = %(user_id)s
)
LIMIT %(limit)s"""
        records = self.execute(sql, {"user_id": user_id, "limit": limit})
        models = [ModelwithmAP.from_clickhouse(record) for record in records]
        return {
            keyword: [[m.model_id, m.mAP] for m in models_]
            for keyword, models_ in groupby(models, "keyword")
        }

    def get_recommend_keywords(
        self, user_id: int, dataset_ids: List[int], limit: int = 10
    ) -> Any:
        sql = """\
SELECT
    keyword_ids,
    sum(keyword_count) AS ref_count
FROM
(
    SELECT
        keyword_ids,
        count(keyword_ids) AS keyword_count
    FROM dataset_keywords
ARRAY JOIN keyword_ids
    WHERE user_id = %(user_id)s AND dataset_id IN (%(dataset_ids)s)
    GROUP BY
        dataset_id,
        keyword_ids
)
GROUP BY keyword_ids
ORDER BY ref_count DESC
LIMIT %(limit)s"""
        return self.execute(
            sql, {"user_id": user_id, "dataset_ids": dataset_ids, "limit": limit}
        )

    def get_task_count(
        self,
        user_id: int,
        precision: str,
        start_at: datetime,
        end_at: datetime,
        limit: int = 10,
    ) -> Dict:
        """
        Get tasks distribution across given precision

        user_id: task owner
        precision: day, week or month
        limit: data points count
        """
        step = 1
        if precision == "month":
            sql = f"""\
WITH
    toDate(0) AS start_date,
    toRelativeMonthNum(start_date) AS relative_month_of_start_date
SELECT
    type,
    task_count,
    addMonths(start_date, relative_month - relative_month_of_start_date) AS time
FROM
(
    SELECT
        toRelativeMonthNum(created_time) AS relative_month,
        type,
        count(type) AS task_count
    FROM task_create
    WHERE user_id = %(user_id)s
    GROUP BY
        type,
        relative_month
    ORDER BY relative_month ASC WITH FILL
        FROM toRelativeMonthNum(toDate(%(start_at)s))
        TO toRelativeMonthNum(toDate(%(end_at)s)) STEP {step}
)
ORDER BY time ASC"""
        else:
            if precision == "week":
                step = 7
            sql = f"""\
SELECT
    type,
    count(type) as task_count,
    toDate(toStartOfInterval(created_time, INTERVAL 1 {precision})) AS time
FROM task_create
WHERE user_id = %(user_id)s
GROUP BY
    type,
    time
ORDER BY time ASC WITH FILL
    FROM toDate(%(start_at)s)
    TO toDate(%(end_at)s) STEP {step}"""

        records = self.execute(
            sql,
            {
                "user_id": user_id,
                "start_at": start_at,
                "end_at": end_at,
                "limit": limit,
            },
        )
        return prepare_task_count(records, limit)

    def close(self) -> None:
        logger.debug("clickhouse client closed")


def prepare_task_count(records: List, limit: int) -> Dict:
    times = []
    defaults = {type_.value: 0 for type_ in TaskType}
    stats = []
    for dt, tasks in groupby([TaskCount.from_clickhouse(r) for r in records], "time"):
        times.append(dt)
        task_count = dict(defaults)
        task_count.update(
            {TaskType[task.type_].value: task.count for task in tasks if task.type_}
        )
        stats.append(task_count)
    return {"task": stats[-limit:], "task_timestamps": times[-limit:]}
