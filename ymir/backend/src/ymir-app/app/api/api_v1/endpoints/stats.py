from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.utils.clickhouse import YmirClickHouse
from app.utils.stats import RedisStats

router = APIRouter()


class StatsPrecision(str, Enum):
    day = "day"
    week = "week"
    month = "month"


@router.get("/datasets/hot", response_model=schemas.StatsPopularDatasetsOut)
def get_most_popular_datasets(
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Get top datasets ordered by ref_count
    """
    stats = clickhouse.get_popular_items(
        current_user.id, column="dataset_ids", limit=limit
    )
    return {"result": stats}


@router.get("/models/hot", response_model=schemas.StatsPopularModelsOut)
def get_most_popular_models(
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Get top models ordered by ref_count
    """
    stats = clickhouse.get_popular_items(
        current_user.id, column="model_ids", limit=limit
    )
    return {"result": stats}


@router.get("/models/map", response_model=schemas.StatsModelmAPsOut)
def get_best_models(
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Get models of highest mAP score, grouped by keyword
    """
    stats = clickhouse.get_models_order_by_map(current_user.id, limit=limit)
    return {"result": stats}


@router.get("/keywords/hot", response_model=schemas.StatsPopularKeywordsOut)
def get_most_popular_keywords(
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Get top keywords ordered by ref_count
    """
    stats = clickhouse.get_popular_items(
        current_user.id, column="keyword_ids", limit=limit
    )
    return {"result": stats}


@router.get("/keywords/recommend", response_model=schemas.StatsKeywordsRecommendOut)
def recommend_keywords(
    dataset_ids: str = Query(
        ..., description="recommend keywords based on given datasets", example="1,2,3"
    ),
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Recommend top keywords based on datasets
    """
    dataset_ids_ = [int(id_) for id_ in dataset_ids.split(",")]
    stats = clickhouse.get_recommend_keywords(
        current_user.id, dataset_ids=dataset_ids_, limit=limit
    )
    return {"result": stats}


@router.get("/tasks/count", response_model=schemas.StatsTasksCountOut)
def get_tasks_count(
    precision: StatsPrecision = Query(..., description="day, week or month"),
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
) -> Any:
    """
    Get tasks count grouped by task_type, divided by time ranges
    """
    end_at = datetime.now()
    start_at = end_at.replace(end_at.year - 1)
    stats = clickhouse.get_task_count(
        current_user.id,
        precision=precision.value,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )
    return {"result": stats}


class StatsType(str, Enum):
    dataset = "dataset"
    model = "model"
    task = "task"


@router.get("/", response_model=schemas.StatsOut, deprecated=True)
def get_stats(
    stats_client: RedisStats = Depends(deps.get_stats_client),
    q: StatsType = Query(..., description="the stats to query"),
    precision: Optional[StatsPrecision] = Query(None, description="day, week or month"),
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get stats of dataset, model or task

    q:
    - dateset
    - model
    - task

    precision:
    - day
    - week
    - month

    You can combine multiple query string with repeated query string, like this:
    GET /api/v1/stats/?q=dataset&q=model
    """
    stats = {}  # type: Dict[str, Any]

    if q is StatsType.dataset:
        stats["dataset"] = stats_client.get_top_datasets(current_user.id, limit=limit)
    if q is StatsType.model:
        stats["model"] = stats_client.get_keyword_wise_best_models(
            current_user.id, limit=limit
        )

    if q is StatsType.task:
        precision = precision or StatsPrecision.day
        task_stats_dict = stats_client.get_task_stats(
            current_user.id, precision.value, limit
        )
        ordered_keys = list(task_stats_dict.keys())
        ordered_keys.sort(reverse=True)
        stats["task"] = [task_stats_dict[k] for k in ordered_keys]
        stats["task_timestamps"] = ordered_keys

    return {"result": stats}
