""" emtry point for pymir-ed (pymir events dispatcher) service """

from collections import defaultdict
import json
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import socketio
from fastapi_socketio import SocketManager

from ed_src import entities
from ed_src.event_dispatcher import EventDispatcher


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
        data = jsonable_encoder(tid_to_taskstates)
        await sio.emit(event='update_taskstate', data=data, namespace=f"/{uid}")


# event dispatcher
ed = EventDispatcher(event_name='/events/taskstates')

# main service and api implememtations
app = FastAPI()


# fastapi handlers
@app.post('/events/taskstates', response_model=entities.EventResp)
async def post_task_states(tid_to_taskstates: Dict[str, entities.TaskState]) -> entities.EventResp:
    try:
        ed.add_event(event_topic='raw', event_body=json.dumps(jsonable_encoder(tid_to_taskstates)))
        await _send_to_socketio(app.sio, tid_to_taskstates=tid_to_taskstates)
    except BaseException:
        logging.exception(msg='handle post_task_states error')
    return entities.EventResp(return_code=0, return_msg=f"done, received: {len(tid_to_taskstates)} tasks")


# sio handlers
# sio = socketio.AsyncServer(async_mode='asgi')
# sio_app = socketio.ASGIApp(sio)
# app.mount(path='/ws', app=sio_app)
socket_manager = SocketManager(app=app)
