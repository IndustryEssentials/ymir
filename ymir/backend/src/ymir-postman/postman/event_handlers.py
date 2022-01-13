import json
import logging
import time
import traceback
from typing import Any, List, Set, Dict, Tuple

import aiohttp
import asyncio
from fastapi.encoders import jsonable_encoder
from pydantic import parse_raw_as

from postman import entities, event_dispatcher  # type: ignore
from postman.settings import settings


redis_connect = event_dispatcher.EventDispatcher.get_redis_connect()


def on_task_state(ed: event_dispatcher.EventDispatcher, mid_and_msgs: list, **kwargs: Any) -> None:
    """
    Returns:
        message ids to be deleted from this stream
    """
    _, msgs = zip(*mid_and_msgs)
    tid_to_taskstates_latest = _select_latest(msgs)
    logging.debug(f"latest: {tid_to_taskstates_latest}")

    # update db, if error occured, write back
    try:
        failed_tids = asyncio.run(_update_db(tid_to_tasks=tid_to_taskstates_latest))
        logging.debug(f"failed_tids: {failed_tids}")
        _save_failed(failed_tids=failed_tids, tid_to_taskstates_latest=tid_to_taskstates_latest)
    except BaseException:
        logging.exception(msg='error occured when async run _update_db')
        # write back all
        _save_failed(failed_tids=set(tid_to_taskstates_latest.keys()),
                     tid_to_taskstates_latest=tid_to_taskstates_latest)


def _select_latest(msgs: List[Dict[str, str]]) -> Dict[str, entities.TaskState]:
    """
    for all redis stream msgs, deserialize them to entities, select the latest for each tid
    """
    logging.debug('_select_latest begins')
    tid_to_taskstates_latest: Dict[str, entities.TaskState] = _load_failed()
    logging.debug(f"_select_latest: previous failed: {list(tid_to_taskstates_latest.keys())}")
    for msg in msgs:
        msg_topic = msg['topic']
        if msg_topic != 'raw' and msg_topic != 'selected':
            continue

        tid_to_taskstates = parse_raw_as(Dict[str, entities.TaskState], msg['body'])
        for tid, taskstate in tid_to_taskstates.items():
            if (tid not in tid_to_taskstates_latest
                    or tid_to_taskstates_latest[tid].percent_result.timestamp < taskstate.percent_result.timestamp):
                tid_to_taskstates_latest[tid] = taskstate
    return tid_to_taskstates_latest


def _save_failed(failed_tids: Set[str], tid_to_taskstates_latest: Dict[str, entities.TaskState]) -> None:
    """
    save failed taskstates to redis cache

    Args:
        failed_tids (Set[str])
        tid_to_taskstates_latest (Dict[str, entities.TaskState])
    """
    # pass
    failed_tid_to_tasks = {tid: tid_to_taskstates_latest[tid] for tid in failed_tids}
    json_str = json.dumps(jsonable_encoder(failed_tid_to_tasks))
    redis_connect.set(name=settings._RETRY_CACHE_KEY, value=json_str)
    logging.debug(f"_save_failed tids: {failed_tids}")


def _load_failed() -> Dict[str, entities.TaskState]:
    """
    load failed taskstates from redis cache

    Returns:
        Dict[str, entities.TaskState]: [description]
    """
    # pass
    json_str = redis_connect.get(name=settings._RETRY_CACHE_KEY)
    logging.debug(f"_load_failed: {json_str}")
    if not json_str:
        return {}
    earlest_timestamp = time.time() - settings._IGNORE_FAILED_SECONDS
    failed_tid_to_taskstates = parse_raw_as(Dict[str, entities.TaskState], json_str)
    failed_tid_to_taskstates = {
        tid: taskstate
        for tid, taskstate in failed_tid_to_taskstates.items()
        if taskstate.percent_result.timestamp >= earlest_timestamp
    }
    return failed_tid_to_taskstates or {}


async def _update_db(tid_to_tasks: Dict[str, entities.TaskState]) -> Set[str]:
    """
    update db for all tasks in tid_to_tasks

    Args:
        tid_to_tasks (Dict[str, entities.TaskState]): key: tid, value: TaskState

    Returns:
        Set[str]: failed tids
    """
    failed_tids: Set[str] = set()
    custom_headers = {'api-key': settings.API_KEY_SECRET}
    logging.debug(f"custom_headers: {custom_headers}")
    async with aiohttp.ClientSession(headers=custom_headers) as session:
        # post them all
        ret = await asyncio.gather(*[_update_db_single_task(session, tid, task) for tid, task in tid_to_tasks.items()],
                                   return_exceptions=True)
        # if all done, return failed tids
        for tid, *_, need_retry in ret:
            if need_retry:
                failed_tids.add(tid)
        return failed_tids


async def _update_db_single_task(session: aiohttp.ClientSession, tid: str,
                                 task: entities.TaskState) -> Tuple[str, str, bool]:
    """
    update db for single task

    Args:
        session (aiohttp.ClientSession): aiohttp client session
        tid (str): task id
        task (entities.TaskState): task state

    Returns:
        Tuple[str, str, bool]: tid, error_message, need_to_retry
    """
    url = f"http://{settings.API_HOST}/api/v1/tasks/status"
    try:
        # task_data: see api: /api/v1/tasks/status
        task_data = {
            'hash': tid,
            'timestamp': task.percent_result.timestamp,
            'state': entities.task_state_str_to_enum(task.percent_result.state),
            'percent': task.percent_result.percent,
            'state_message': task.percent_result.state_message
        }
        async with session.post(url=url, json=task_data) as response:
            logging.debug(f"_update_db_single_task: request: {task_data}")
            response_text = await response.text()
            logging.debug(f"_update_db_single_task: response: {response_text}")
            response_obj = json.loads(response_text)

            return_code = int(response_obj['code'])
            return_msg = response_obj.get('message', '')
            return (tid, return_msg, return_code != settings._APP_RC_TASK_NOT_FOUND)
    except BaseException as e:
        logging.debug(traceback.format_exc())
        return (tid, f"{type(e).__name__}: {e}", True)
