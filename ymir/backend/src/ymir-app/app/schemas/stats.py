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
