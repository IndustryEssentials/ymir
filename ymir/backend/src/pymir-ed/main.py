""" emtry point for pymir-ed (pymir events dispatcher) service """

from typing import Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel


# data models: req
class TaskStateExtra(BaseModel):
    user_id: str
    monitor_type: int
    log_path: str
    description: Optional[str]


class TaskStatePercent(BaseModel):
    task_id: str
    timestamp: int
    percent: float
    state: str
    state_code: int
    state_message: Optional[str]
    stack_error_info: Optional[str]


class TaskState(BaseModel):
    task_extra_info: TaskStateExtra
    percent_result: TaskStatePercent


class TaskStatesEvent(BaseModel):
    task_states: Dict[str, TaskState]


# data models: resp
class EventResp(BaseModel):
    return_code: int
    return_msg: str


# main service and api implememtations
app_ed = FastAPI()


@app_ed.post('/events/taskstates', response_model=EventResp)
async def root(tse: Dict[str, TaskState]) -> EventResp:
    return EventResp(return_code=0, return_msg=f"done, received: {len(tse)} tasks")
