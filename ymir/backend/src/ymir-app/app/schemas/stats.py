from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel

from .common import Common


class Stats(BaseModel):
    dataset: Optional[List]
    model: Optional[Dict[str, List[Tuple[int, float]]]]
    task: Optional[List]
    task_timestamps: Optional[List]


class StatsOut(Common):
    result: Stats


class StatsPopularDatasetsOut(Common):
    result: List[Tuple[int, int]]


class StatsPopularModelsOut(Common):
    result: List[Tuple[int, int]]


class StatsPopularKeywordsOut(Common):
    result: List[Tuple[str, int]]


class StatsKeywordsRecommendOut(Common):
    result: List[Tuple[str, int]]


class StatsTasksCount(BaseModel):
    task: Optional[List[Dict[str, int]]]
    task_timestamps: Optional[List]


class StatsTasksCountOut(Common):
    result: StatsTasksCount


class StatsModelmAPsOut(Common):
    result: Dict[str, List[Tuple[int, float]]]
