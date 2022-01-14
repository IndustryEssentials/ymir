import json
import logging
import requests
import time
from typing import Any, List, Set, Dict, Tuple

from fastapi.encoders import jsonable_encoder
from pydantic import parse_raw_as

from controller.utils import tasks_util
from postman import entities, event_dispatcher  # type: ignore
from postman.settings import settings

redis_connect = event_dispatcher.EventDispatcher.get_redis_connect()


def on_task_state(ed: event_dispatcher.EventDispatcher, mid_and_msgs: list, **kwargs: Any) -> None:
    """
    Returns:
        message ids to be deleted from this stream
    """
    _, msgs = zip(*mid_and_msgs)
    tid_to_taskstates_latest = _aggregate_msgs(msgs)
    logging.debug(f"latest: {tid_to_taskstates_latest}")

    # update db, if error occured, write back
    failed_tids = None
    try:
        failed_tids = _update_db(tid_to_tasks=tid_to_taskstates_latest)
        _save_failed(failed_tids=failed_tids, tid_to_taskstates_latest=tid_to_taskstates_latest)
    except BaseException:
        logging.exception(msg='error occured when async run _update_db')
        # write back all
        failed_tids = set(tid_to_taskstates_latest.keys())
        _save_failed(failed_tids=failed_tids, tid_to_taskstates_latest=tid_to_taskstates_latest)

    if failed_tids:
        time.sleep(5)


def _aggregate_msgs(msgs: List[Dict[str, str]]) -> Dict[str, entities.TaskState]:
    """
    for all redis stream msgs, deserialize them to entities, select the latest for each tid
    """
    tid_to_taskstates_latest: Dict[str, entities.TaskState] = _load_failed()
    logging.debug(f"_aggregate_msgs: previous failed: {list(tid_to_taskstates_latest.keys())}")
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
    failed_tid_to_tasks = {tid: tid_to_taskstates_latest[tid] for tid in failed_tids}
    json_str = json.dumps(jsonable_encoder(failed_tid_to_tasks))
    redis_connect.set(name=settings.RETRY_CACHE_KEY, value=json_str)
    logging.debug(f"_save_failed: {failed_tids}")


def _load_failed() -> Dict[str, entities.TaskState]:
    """
    load failed taskstates from redis cache

    Returns:
        Dict[str, entities.TaskState]: [description]
    """
    # pass
    json_str = redis_connect.get(name=settings.RETRY_CACHE_KEY)
    logging.debug(f"_load_failed: {json_str}")
    if not json_str:
        return {}
    failed_tid_to_taskstates = parse_raw_as(Dict[str, entities.TaskState], json_str)
    return failed_tid_to_taskstates or {}


def _update_db(tid_to_tasks: Dict[str, entities.TaskState]) -> Set[str]:
    """
    update db for all tasks in tid_to_tasks

    Args:
        tid_to_tasks (Dict[str, entities.TaskState]): key: tid, value: TaskState

    Returns:
        Set[str]: failed tids
    """
    failed_tids: Set[str] = set()
    custom_headers = {'api-key': settings.APP_API_KEY}
    for tid, task in tid_to_tasks.items():
        *_, need_retry = _update_db_single_task(tid, task, custom_headers)
        if need_retry:
            failed_tids.add(tid)
    return failed_tids


def _update_db_single_task(tid: str, task: entities.TaskState, custom_headers: dict) -> Tuple[str, str, bool]:
    """
    update db for single task

    Args:
        tid (str): task id
        task (entities.TaskState): task state
        custom_headers (dict)

    Returns:
        Tuple[str, str, bool]: tid, error_message, need_to_retry
    """
    url = f"http://{settings.APP_API_HOST}/api/v1/tasks/status"
    try:
        # task_data: see api: /api/v1/tasks/status
        task_data = {
            'hash': tid,
            'timestamp': task.percent_result.timestamp,
            'state': tasks_util.task_state_str_to_code(task.percent_result.state),
            'percent': task.percent_result.percent,
            'state_message': task.percent_result.state_message
        }

        logging.info(f"_update_db_single_task: request: {task_data}")
        response = requests.post(url=url, headers=custom_headers, json=task_data)
        logging.info(f"_update_db_single_task: response: {response.text}")

        response_obj = json.loads(response.text)
        return_code = int(response_obj['code'])
        return_msg = response_obj.get('message', '')

        return (tid, return_msg, return_code != 0)
    except requests.exceptions.RequestException as e:
        logging.exception(msg='_update_db_single_task error')
        return (tid, f"{type(e).__name__}: {e}", True)
