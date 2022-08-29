from enum import Enum
import logging
import json
from typing import Any, Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.utils.ymir_viz import VizClient
from common_utils.labels import UserLabels

router = APIRouter()


class StatsPrecision(str, Enum):
    day = "day"
    week = "week"
    month = "month"


@router.get("/keywords/recommend", response_model=schemas.StatsMetricsQueryOut)
def recommend_keywords(
    dataset_ids: str = Query(None, description="recommend keywords based on given datasets", example="1,2,3"),
    limit: int = Query(10, description="limit the data point size"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    viz_client: VizClient = Depends(deps.get_viz_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Recommend top keywords based on history tasks.
    """
    keyword_ids: Optional[List[int]] = None
    if dataset_ids:
        datasets = crud.dataset.get_multi_by_ids(db, ids=[int(i) for i in dataset_ids.split(",")])
        keywords = extract_keywords(datasets)
        keyword_ids = user_labels.get_class_ids(keywords)

    # todo pass keyword_ids to viewer as params
    stats = viz_client.query_metrics(
        metrics_group="task",
        user_id=current_user.id,
        query_field="key_ids",
        bucket="count",
        limit=limit,
        keyword_ids=keyword_ids,
    )
    for element in stats:
        element["legend"] = user_labels.get_main_name(int(element["legend"]))
    logging.info(f"viz stats: {stats}")
    return {"result": stats}


@router.get("/projects/count", response_model=schemas.StatsMetricsQueryOut)
def get_projects_count(
    precision: StatsPrecision = Query(..., description="day, week or month"),
    limit: int = Query(10, description="limit the data point size"),
    current_user: models.User = Depends(deps.get_current_active_user),
    viz_client: VizClient = Depends(deps.get_viz_client),
) -> Any:
    """
    Get projects count divided by time ranges
    """
    stats = viz_client.query_metrics(
        metrics_group="task",
        user_id=current_user.id,
        query_field="create_time",
        bucket="time",
        unit=precision.value,
        limit=limit,
    )

    logging.info(f"viz stats: {stats}")
    return {"result": stats}


def extract_keywords(datasets: List[models.Dataset]) -> List[str]:
    """
    dataset got keywords column which contains:
    {
      "gt": {"keyword": count},
      "pred": {"keyword": count},
    }

    extract all the keywords in gt and pred
    """
    datasets_keywords = [json.loads(dataset.keywords) for dataset in datasets if dataset.keywords]
    keywords = {
        k
        for dataset_keywords in datasets_keywords
        for k in (list(dataset_keywords["gt"]) + list(dataset_keywords["pred"]))
    }
    return list(keywords)
