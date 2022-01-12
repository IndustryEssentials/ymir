""" emtry point for pymir-ed (pymir events dispatcher) service """

from collections import defaultdict
import json
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
import socketio
from fastapi_socketio import SocketManager

from events_src import entities
from events_src.event_dispatcher import EventDispatcher


# private: socketio
async def _sort_by_user_id(
        tid_to_taskstates: Dict[str, entities.TaskState]) -> Dict[str, Dict[str, entities.TaskState]]:
    """
    returns: Dict[str, Dict[str, dict]]
                  (uid)     (tid) (TaskState)
    """
    uid_to_tasks = defaultdict(dict)
    for tid, taskstate in tid_to_taskstates.items():
        uid = taskstate.task_extra_info.user_id
        uid_to_tasks[uid][tid] = taskstate
    return uid_to_tasks


async def _send_to_socketio(sio: socketio.Server, tid_to_taskstates: Dict[str, entities.TaskState]) -> None:
    uid_to_taskstates = await _sort_by_user_id(tid_to_taskstates)
    for uid, tid_to_taskstates in uid_to_taskstates.items():
        data = {}
        for tid, taskstate in tid_to_taskstates.items():
            data[tid] = {}
            data[tid]['state'] = entities.task_state_str_to_enum(taskstate.percent_result.state)
            data[tid]['percent'] = taskstate.percent_result.percent
            data[tid]['timestamp'] = taskstate.percent_result.timestamp
            data[tid]['state_code'] = taskstate.percent_result.state_code
            data[tid]['state_message'] = taskstate.percent_result.state_message
            data[tid]['stack_error_info'] = taskstate.percent_result.stack_error_info
        await sio.emit(event='update_taskstate', data=data, namespace=f"/{uid}")
        print(f"sent update_taskstate: {data} -> /{uid}")


# event dispatcher
ed = EventDispatcher(event_name='/events/taskstates')

# main service and api implememtations
app = FastAPI(title='event dispatcher')
backend_cors_origions = [
    "http://192.168.34.88:8000", "http://192.168.13.252:8089", "http://192.168.13.107:8089",
    "http://192.168.13.108:8089", "http://192.168.34.193:8000", "http://192.168.57.41:8000"
]  # for test
if backend_cors_origions:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=backend_cors_origions,
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
async def post_task_states(tid_to_taskstates: Dict[str, entities.TaskState]) -> entities.EventResp:
    try:
        ed.add_event(event_topic='raw', event_body=json.dumps(jsonable_encoder(tid_to_taskstates)))
        await _send_to_socketio(app.sio, tid_to_taskstates=tid_to_taskstates)
    except BaseException:
        logging.exception(msg='handle post_task_states error')
    return entities.EventResp(return_code=0, return_msg=f"done, received: {len(tid_to_taskstates)} tasks")
