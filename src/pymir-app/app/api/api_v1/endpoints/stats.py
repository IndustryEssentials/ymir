from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.utils.stats import RedisStats

router = APIRouter()


class StatsType(str, Enum):
    dataset = "dataset"
    model = "model"
    task = "task"


class StatsPrecision(str, Enum):
    day = "day"
    week = "week"
    month = "month"


@router.get("/", response_model=schemas.StatsOut)
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
    stats = {}

    if q is StatsType.dataset:
        stats["dataset"] = stats_client.get_top_datasets(current_user.id, limit=limit)
    if q is StatsType.model:
        stats["model"] = stats_client.get_keyword_wise_best_models(current_user.id, limit=limit)  # type: ignore

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
