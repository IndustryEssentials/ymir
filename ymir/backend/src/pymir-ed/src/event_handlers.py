import json
import os
import traceback
from typing import List, Set, Dict, Tuple

import aiohttp
import asyncio
from fastapi.encoders import jsonable_encoder
from pydantic import parse_raw_as

from src import entities, event_dispatcher


def on_task_state(ed: event_dispatcher.EventDispatcher, mid_and_msgs: list, **kwargs) -> None:
    """
    Returns:
        message ids to be deleted from this stream
    """
    _, msgs = zip(*mid_and_msgs)
    tid_to_taskstates_latest = _select_latest(msgs)

    _update_socketio_clients(tid_to_taskstates_latest)

    # update db, if error occured, write back
    try:
        failed_tids = asyncio.run(_update_db(tid_to_tasks=tid_to_taskstates_latest))
        # write back failed
        if failed_tids:
            _write_back(ed=ed, failed_tids=failed_tids, tid_to_taskstates_latest=tid_to_taskstates_latest)
    except BaseException:
        traceback.print_exc()
        # write back all
        _write_back(ed=ed,
                    failed_tids=tid_to_taskstates_latest.keys(),
                    tid_to_taskstates_latest=tid_to_taskstates_latest)


def _select_latest(msgs: List[Dict[str, str]]) -> Dict[str, entities.TaskState]:
    """
    for all redis stream msgs, deserialize them to entities, select the latest for each tid
    """
    tid_to_taskstates_latest: Dict[str, entities.TaskState] = {}
    for msg in msgs:
        tid_to_taskstates = parse_raw_as(Dict[str, entities.TaskState], msg['body'])
        for tid, taskstate in tid_to_taskstates.items():
            if (tid not in tid_to_taskstates_latest
                    or tid_to_taskstates_latest[tid].percent_result.timestamp < taskstate.percent_result.timestamp):
                tid_to_taskstates_latest[tid] = taskstate
    return tid_to_taskstates_latest


def _write_back(ed: event_dispatcher.EventDispatcher, failed_tids: Set[str],
                tid_to_taskstates_latest: Dict[str, entities.TaskState]):
    failed_tid_to_tasks = {tid: tid_to_taskstates_latest[tid].dict() for tid in failed_tids}
    print(f"failed json: {json.dumps(failed_tid_to_tasks)}")
    # ed.add_event(event_topic='selected', event_body=json.dumps(failed_tid_to_tasks))


# def _sort_by_user_id(tasks: dict) -> Dict[str, Dict[str, dict]]:
#     """
#     returns: Dict[str, Dict[str, dict]]
#                   (uid)     (tid) (percent results)
#     """
#     uid_to_tasks = defaultdict(dict)
#     for tid, task in tasks.items():
#         uid = task['task_extra_info']['user_id']
#         percent_result = task['percent_result']
#         uid_to_tasks[uid][tid] = percent_result
#     return uid_to_tasks


async def _update_db(tid_to_tasks: Dict[str, entities.TaskState]) -> Set[str]:
    failed_tids: Set[str] = set()
    custom_headers = {'api-key': os.environ.get("API_KEY_SECRET", "fake-api-key")}  # TODO
    async with aiohttp.ClientSession(headers=custom_headers) as session:
        # post them all
        ret = await asyncio.gather(*[_update_db_single_task(session, tid, task) for tid, task in tid_to_tasks.items()],
                                   return_exceptions=True)
        # if all done, return failed tids
        for tid, error_msg in ret:
            if error_msg:
                failed_tids.add(tid)
        return failed_tids


async def _update_db_single_task(session: aiohttp.ClientSession, tid: str, task: entities.TaskState) -> Tuple[str, str]:
    url = '127.0.0.1:9999/api/v1/tasks/status'  # TODO: INTO CONFIG
    try:
        # task_data: see api: /api/v1/tasks/status
        task_data = {
            'hash': tid,
            'timestamp': task.percent_result.timestamp,
            'state': task.percent_result.state,
            'percent': task.percent_result.percent,
            'state_message': task.percent_result.state_message
        }
        async with session.post(url=url, data=json.dumps(task_data)) as response:
            return_code = int(response['code'])
            return (tid, ('' if return_code == 0 else f"error: {return_code}: {response.get('message', '')}"))
    except BaseException as e:
        return (tid, f"connection failed: {e}")


def _update_socketio_clients(tid_to_tasks: Dict[str, entities.TaskState]) -> None:
    pass
