from collections import defaultdict
import json
import os
import traceback
from typing import Set, Dict, Tuple

import aiohttp
import asyncio
from src import event_dispatcher


# TODO: WRITE AS FASTAPI DECORATOR
def on_task_state(ed: event_dispatcher.EventDispatcher, msg_id: str, msg_topic: str, msg_body: str) -> None:
    print(f"on_task_state: {msg_body}")
    if msg_topic == 'raw':
        _on_raw_task_state(json.loads(msg_body))
    elif msg_topic == 'writeback':
        _on_writeback_task_state(json.loads(msg_body))
    # other topics: ignore


def _on_raw_task_state(msg_body: dict) -> None:
    uid_to_tasks = _sort_by_user_id(msg_body)

    # send socket io to clients
    for uid, tasks in uid_to_tasks.items():
        _update_socketio_clients(uid=uid, tid_to_task=tasks)

    # update db, if error occured, write back
    try:
        failed_tids = asyncio.run(_update_db(tid_to_tasks=msg_body))
        print(f"failed: {failed_tids}")
        if failed_tids:
            # TODO: WRITE BACK
            pass
    except BaseException:
        traceback.print_exc()
        # TODO: WRITE BACK ALL
        pass


def _on_writeback_task_state(msg_body: dict) -> None:
    pass


def _sort_by_user_id(tasks: dict) -> Dict[str, Dict[str, dict]]:
    """
    returns: Dict[str, Dict[str, dict]]
                  (uid)     (tid) (percent results)
    """
    uid_to_tasks = defaultdict(dict)
    for tid, task in tasks.items():
        uid = task['task_extra_info']['user_id']
        percent_result = task['percent_result']
        uid_to_tasks[uid][tid] = percent_result
    return uid_to_tasks


async def _update_db(tid_to_tasks: dict) -> Set[str]:
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


async def _update_db_single_task(session: aiohttp.ClientSession, tid: str, task: dict) -> Tuple[str, str]:
    url = '127.0.0.1:9999/api/v1/tasks/status'  # TODO: INTO CONFIG
    try:
        async with session.post(url=url, data=json.dumps(task)) as response:
            return_code = int(response['code'])
            return (tid, ('' if return_code == 0 else f"error: {return_code}: {response.get('message', '')}"))
    except BaseException as e:
        return (tid, f"connection failed: {e}")


def _update_socketio_clients(uid: str, tid_to_task: dict) -> None:
    pass
