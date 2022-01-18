""" emtry point for pymir-ed (pymir events dispatcher) service """

import asyncio
import json
import logging
from typing import List

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi_socketio import SocketManager
from starlette.middleware.cors import CORSMiddleware

from postman import entities
from postman.event_dispatcher import EventDispatcher
from postman.settings import constants, settings


uvicorn_logger = logging.getLogger("uvicorn")


# main service and api implememtations
app = FastAPI(title=constants.PROJECT_NAME)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # binded to /ws by default
    # if use with fastapi and cors settings
    #   cors_allowed_origins set to []: https://github.com/pyropy/fastapi-socketio/issues/28
    socket_manager = SocketManager(app=app, cors_allowed_origins=[])
else:
    socket_manager = SocketManager(app=app)


# fastapi handlers
@app.post('/events/taskstates', response_model=entities.EventResp)
def post_task_states(tid_to_taskstates: entities.TaskStateDict) -> entities.EventResp:
    EventDispatcher.add_event(event_name='/events/taskstates',
                              event_topic='raw',
                              event_body=json.dumps(jsonable_encoder(tid_to_taskstates)))

    return entities.EventResp(return_code=0, return_msg=f"done, received: {len(tid_to_taskstates)} tasks")


@app.post('/events/push', response_model=entities.EventResp)
def post_events_push(event_payloads: List[entities.EventPayload]) -> entities.EventResp:
    for payload in event_payloads:
        asyncio.run(app.sio.emit(event=payload.event, data=payload.data, namespace=payload.namespace))
    return entities.EventResp(return_code=0, return_msg='done')
