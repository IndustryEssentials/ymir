from typing import Dict, List, Optional

from pydantic import BaseModel

from .common import Common


class Stats(BaseModel):
    dataset: Optional[List]
    model: Optional[List]
    task: Optional[List]
    task_timestamps: Optional[List]


class StatsOut(Common):
    result: Stats
