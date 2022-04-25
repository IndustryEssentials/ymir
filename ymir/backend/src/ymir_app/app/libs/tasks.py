import itertools
import asyncio
from typing import Dict, List, Tuple

import aiohttp

from app.config import settings
from app import schemas
from app.api.errors.errors import FailedToUpdateTaskStatus


class Retry(Exception):
    pass


async def should_retry(resp: aiohttp.ClientResponse) -> bool:
    if not resp.ok:
        # server returned 500, for example
        return True
    response = await resp.json()
    if int(response["code"]) == FailedToUpdateTaskStatus.code:
        # server explicitly asked for retry
        return True
    return False


async def post_task_update(session: aiohttp.ClientSession, payload: Dict) -> None:
    async with session.post(
        "http://localhost/api/v1/tasks/status", json=payload, headers={"api-key": settings.APP_API_KEY}
    ) as resp:
        if await should_retry(resp):
            raise Retry()


async def batch_update_task_status(events: List[Tuple[str, Dict]]) -> List[str]:
    ids, payloads = [], []
    for id_, msg in events:
        ids.append(id_)
        payloads.append(schemas.TaskUpdateStatus.from_monitor_event(msg["payload"]).dict())

    async with aiohttp.ClientSession() as session:
        tasks = [post_task_update(session, payload) for payload in payloads]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_id_selectors = [not isinstance(res, Exception) for res in results]
        return list(itertools.compress(ids, success_id_selectors))
