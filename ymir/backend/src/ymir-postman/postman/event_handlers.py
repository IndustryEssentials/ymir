from collections import defaultdict
import json
import logging
import requests
import time
from typing import Any, List, Set, Dict, Tuple

from fastapi.encoders import jsonable_encoder
from pydantic import parse_raw_as

from postman import entities, event_dispatcher  # type: ignore
from postman.settings import constants, settings


class _UpdateDbResult:
    SUCCESS = 0  # update success
    RETRY = 1  # update failed, need retry
    DROP = 2  # update failed, need drop

    @classmethod
    def code_from_return_code(cls, return_code: int) -> int:
        if return_code == constants.RC_OK:
            return cls.SUCCESS
        elif return_code == constants.RC_FAILED_TO_UPDATE_TASK_STATUS:
            return cls.RETRY
        else:
            return cls.DROP

    def __init__(self) -> None:
        self.success_tids: Set[str] = set()
        self.retry_tids: Set[str] = set()
        self.drop_tids: Set[str] = set()

    def __repr__(self) -> str:
        return f"success: {self.success_tids}, retry: {self.retry_tids}, drop: {self.drop_tids}"


redis_connect = event_dispatcher.EventDispatcher.get_redis_connect()


def on_task_state(ed: event_dispatcher.EventDispatcher, mid_and_msgs: list, **kwargs: Any) -> None:
    _, msgs = zip(*mid_and_msgs)
    tid_to_taskstates_latest = _aggregate_msgs(msgs)
    if not tid_to_taskstates_latest:
        return

    # update db, save failed
    update_db_result = _update_db(tid_to_tasks=tid_to_taskstates_latest)
    _update_sio(tids=update_db_result.success_tids, tid_to_taskstates=tid_to_taskstates_latest)
    if update_db_result.retry_tids:
        time.sleep(5)
    _save_retry(retry_tids=update_db_result.retry_tids, tid_to_taskstates_latest=tid_to_taskstates_latest)


def _aggregate_msgs(msgs: List[Dict[str, str]]) -> entities.TaskStateDict:
    """
    for all redis stream msgs, deserialize them to entities, select the latest for each tid
    """
    tid_to_taskstates_latest: entities.TaskStateDict = _load_retry()
    for msg in msgs:
        msg_topic = msg['topic']
        if msg_topic != constants.EVENT_TOPIC_RAW:
            continue

        tid_to_taskstates = parse_raw_as(entities.TaskStateDict, msg['body'])
        for tid, taskstate in tid_to_taskstates.items():
            if (tid not in tid_to_taskstates_latest
                    or tid_to_taskstates_latest[tid].percent_result.timestamp < taskstate.percent_result.timestamp):
                tid_to_taskstates_latest[tid] = taskstate
    return tid_to_taskstates_latest


# private: update db
def _save_retry(retry_tids: Set[str], tid_to_taskstates_latest: entities.TaskStateDict) -> None:
    """
    save failed taskstates to redis cache

    Args:
        retry_tids (Set[str])
        tid_to_taskstates_latest (entities.TaskStateDict)
    """
    retry_tid_to_tasks = {tid: tid_to_taskstates_latest[tid] for tid in retry_tids if tid in tid_to_taskstates_latest}
    json_str = json.dumps(jsonable_encoder(retry_tid_to_tasks))
    redis_connect.set(name=settings.RETRY_CACHE_KEY, value=json_str)


def _load_retry() -> entities.TaskStateDict:
    """
    load failed taskstates from redis cache

    Returns:
        entities.TaskStateDict
    """
    json_str = redis_connect.get(name=settings.RETRY_CACHE_KEY)
    if not json_str:
        return {}

    return parse_raw_as(entities.TaskStateDict, json_str) or {}


def _update_db(tid_to_tasks: entities.TaskStateDict) -> _UpdateDbResult:
    """
    update db for all tasks in tid_to_tasks

    Args:
        tid_to_tasks (entities.TaskStateDict): key: tid, value: TaskState

    Returns:
        _UpdateDbResult: update db result (success, retry and drop tids)
    """
    update_db_result = _UpdateDbResult()
    custom_headers = {'api-key': settings.APP_API_KEY}
    for tid, task in tid_to_tasks.items():
        *_, code = _update_db_single_task(tid, task, custom_headers)
        if code == _UpdateDbResult.SUCCESS:
            update_db_result.success_tids.add(tid)
        elif code == _UpdateDbResult.RETRY:
            update_db_result.retry_tids.add(tid)
        else:
            update_db_result.drop_tids.add(tid)

    return update_db_result


def _update_db_single_task(tid: str, task: entities.TaskState, custom_headers: dict) -> Tuple[str, int]:
    """
    update db for single task

    Args:
        tid (str): task id
        task (entities.TaskState): task state
        custom_headers (dict)

    Returns:
        Tuple[str, int]: error_message, result code (success, retry or drop)
    """
    url = f"http://{settings.APP_API_HOST}/api/v1/tasks/status"

    # task_data: see api: /api/v1/tasks/status
    task_data = {
        'hash': tid,
        'timestamp': task.percent_result.timestamp,
        'state': task.percent_result.state,
        'percent': task.percent_result.percent,
        'state_message': task.percent_result.state_message
    }

    logging.debug(f"update db single task request: {task_data}")
    try:
        response = requests.post(url=url, headers=custom_headers, json=task_data)
    except requests.exceptions.RequestException as e:
        logging.exception(msg=f"update db single task error ignored: {tid}, {e}")
        return (f"{type(e).__name__}: {e}", _UpdateDbResult.RETRY)

    response_obj = json.loads(response.text)
    return_code = int(response_obj['code'])
    return_msg = response_obj.get('message', '')

    logging.info(f"update db single task response: {tid}, {return_code}, {return_msg}")

    return (return_msg, _UpdateDbResult.code_from_return_code(return_code))


# private: socketio
def _update_sio(tids: Set[str], tid_to_taskstates: entities.TaskStateDict) -> None:
    if not tids:
        return

    event_payloads = _get_event_payloads({tid: tid_to_taskstates[tid] for tid in tids if tid in tid_to_taskstates})

    url = f"{settings.PM_URL}/events/push"
    try:
        requests.post(url=url, json=event_payloads)
    except requests.exceptions.RequestException:
        logging.exception('update sio error ignored')


def _get_event_payloads(tid_to_taskstates: entities.TaskStateDict) -> list:
    # sort by user
    uid_to_taskdatas: Dict[str, Dict[str, Any]] = defaultdict(dict)
    for tid, taskstate in tid_to_taskstates.items():
        uid = taskstate.task_extra_info.user_id
        uid_to_taskdatas[uid][tid] = {
            'state': taskstate.percent_result.state,
            'percent': taskstate.percent_result.percent,
            'timestamp': taskstate.percent_result.timestamp,
            'state_code': taskstate.percent_result.state_code,
            'state_message': taskstate.percent_result.state_message,
            'stack_error_info': taskstate.percent_result.stack_error_info
        }

    # get event payloads
    event_payloads = []
    for uid, tid_to_taskdatas in uid_to_taskdatas.items():
        event_payloads.append({
            'event': 'update_taskstate',
            'namespace': f"/{uid}",
            'data': tid_to_taskdatas
        })
    return event_payloads
