from datetime import datetime
from enum import Enum
import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from app import models, schemas
from app.api import deps
from app.utils.clickhouse import YmirClickHouse
from app.utils.ymir_viz import VizClient
from common_utils.labels import UserLabels

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
    stats = clickhouse.get_popular_items(current_user.id, column="dataset_ids", limit=limit)
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
    stats = clickhouse.get_popular_items(current_user.id, column="model_ids", limit=limit)
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
    stats = clickhouse.get_popular_items(current_user.id, column="keyword_ids", limit=limit)
    return {"result": stats}


# @router.get("/keywords/recommend", response_model=schemas.StatsMetricsQueryOut)
@router.get("/keywords/recommend", response_model=schemas.StatsKeywordsRecommendOut)
def recommend_keywords(
    dataset_ids: str = Query(..., description="recommend keywords based on given datasets", example="1,2,3"),
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
    viz_client: VizClient = Depends(deps.get_viz_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),

) -> Any:
    """
    Recommend top keywords based on history tasks.
    """
    # stats = viz_client.query_metrics(
    #     metrics_group="task",
    #     user_id=current_user.id,
    #     query_field="key_ids",
    #     bucket="count",
    #     limit=limit,
    # )
    # for element in stats["result"]:
    #     element["legend"] = user_labels.get_main_name(int(element["legend"]))
    # logging.info(f"viz stats: {stats}")

    dataset_ids_ = [int(id_) for id_ in dataset_ids.split(",")]
    stats = clickhouse.get_recommend_keywords(current_user.id, dataset_ids=dataset_ids_, limit=limit)
    return {"result": stats}


# @router.get("/projects/count", response_model=schemas.StatsMetricsQueryOut)
@router.get("/projects/count", response_model=schemas.StatsProjectsCountOut)
def get_projects_count(
    precision: StatsPrecision = Query(..., description="day, week or month"),
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    clickhouse: YmirClickHouse = Depends(deps.get_clickhouse_client),
    viz_client: VizClient = Depends(deps.get_viz_client),
) -> Any:
    """
    Get projects count divided by time ranges
    """
    # stats = viz_client.query_metrics(
    #     metrics_group="task",
    #     user_id=current_user.id,
    #     query_field="create_time",
    #     bucket="time",
    #     unit=precision,
    #     limit=limit,
    # )

    end_at = datetime.now()
    start_at = end_at.replace(end_at.year - 1)
    stats = clickhouse.get_project_count(
        current_user.id,
        precision=precision.value,
        start_at=start_at,
        end_at=end_at,
    )
    logging.info(f"viz stats: {stats}")
    return {"result": stats}
