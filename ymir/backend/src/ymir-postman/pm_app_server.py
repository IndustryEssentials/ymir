""" emtry point for pymir-ed (pymir events dispatcher) service """

import asyncio
from collections import defaultdict
import json
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
import socketio
from fastapi_socketio import SocketManager

from controller.utils import tasks_util
from postman import entities
from postman.event_dispatcher import EventDispatcher
from postman.settings import settings


# private: socketio
def _sort_by_user_id(tid_to_taskstates: Dict[str, entities.TaskState]) -> Dict[str, Dict[str, entities.TaskState]]:
    """
    returns: Dict[str, Dict[str, dict]]
                  (uid)     (tid) (TaskState)
    """
    uid_to_tasks = defaultdict(dict)
    for tid, taskstate in tid_to_taskstates.items():
        uid = taskstate.task_extra_info.user_id
        uid_to_tasks[uid][tid] = taskstate
    return uid_to_tasks


def _send_to_socketio(sio: socketio.Server, tid_to_taskstates: Dict[str, entities.TaskState]) -> None:
    uid_to_taskstates = _sort_by_user_id(tid_to_taskstates)
    for uid, tid_to_taskstates in uid_to_taskstates.items():
        data = {}
        for tid, taskstate in tid_to_taskstates.items():
            data[tid] = {
                'state': tasks_util.task_state_str_to_code(taskstate.percent_result.state),
                'percent': taskstate.percent_result.percent,
                'timestamp': taskstate.percent_result.timestamp,
                'state_code': taskstate.percent_result.state_code,
                'state_message': taskstate.percent_result.state_message,
                'stack_error_info': taskstate.percent_result.stack_error_info
            }
        asyncio.run(sio.emit(event='update_taskstate', data=data, namespace=f"/{uid}"))
        print(f"sent update_taskstate: {data} -> /{uid}")


# main service and api implememtations
app = FastAPI(title=settings.PROJECT_NAME)
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
def post_task_states(tid_to_taskstates: Dict[str, entities.TaskState]) -> entities.EventResp:
    EventDispatcher.add_event(event_name='/events/taskstates',
                              event_topic='raw',
                              event_body=json.dumps(jsonable_encoder(tid_to_taskstates)))
    _send_to_socketio(app.sio, tid_to_taskstates=tid_to_taskstates)

    return entities.EventResp(return_code=0, return_msg=f"done, received: {len(tid_to_taskstates)} tasks")
