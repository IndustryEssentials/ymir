""" emtry point for pymir-ed (pymir events dispatcher) service """

import json
from typing import Dict

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder

from src import entities, event_handlers
from src.event_dispatcher import EventDispatcher


# event dispatcher
ed = EventDispatcher(event_name='/events/taskstates')
ed.register_handler(event_handlers.on_task_state)
ed.start()


# main service and api implememtations
app_ed = FastAPI()


# fastapi handlers
@app_ed.post('/events/taskstates', response_model=entities.EventResp)
async def post_task_states(tid_to_taskstates: Dict[str, entities.TaskState]) -> entities.EventResp:
    try:
        ed.add_event(event_topic='raw', event_body=json.dumps(jsonable_encoder(tid_to_taskstates)))
    except Exception as e:
        print(e)
    return entities.EventResp(return_code=0, return_msg=f"done, received: {len(tid_to_taskstates)} tasks")
