""" emtry point for pymir-ed (pymir events dispatcher) service """

import json
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src import event_handlers
from src.event_dispatcher import EventDispatcher


# data models: req
class TaskStateExtra(BaseModel):
    user_id: str
    monitor_type: int
    log_path: List[str]
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


# data models: resp
class EventResp(BaseModel):
    return_code: int
    return_msg: str


# event dispatcher
ed = EventDispatcher(event_name='/events/taskstates')
ed.register_handler(event_handlers.on_task_state)
ed.start()


# main service and api implememtations
app_ed = FastAPI()


@app_ed.post('/events/taskstates', response_model=EventResp)
async def post_task_states(tse: Dict[str, TaskState]) -> EventResp:
    try:
        ed.add_event(event_topic='raw', event_body=json.dumps(jsonable_encoder(tse)))
    except Exception as e:
        print(e)
    return EventResp(return_code=0, return_msg=f"done, received: {len(tse)} tasks")
