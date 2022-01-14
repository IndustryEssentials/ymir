import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from aiohttp import ClientSession
from arq import cron
from arq.connections import RedisSettings

env = os.environ.get

CHECK_INTERVAL_IN_SECONDS = int(env("CHECK_INTERVAL_IN_SECONDS", 30))
API_HOST = env("API_HOST", "backend")
REDIS_URI = env("BACKEND_REDIS_URI", "redis://redis:6379")
API_KEY_SECRET = env("API_KEY_SECRET")


async def update_task_status(ctx: Dict) -> int:
    """
    POST /tasks/update_status
    to check all the unfinished tasks
    """
    session = ClientSession()

    api_url = f"http://{API_HOST}/api/v1/tasks/update_status"
    headers = {"api-key": API_KEY_SECRET}
    logging.info("updating tasks status... %s" % api_url)
    async with session.post(api_url, headers=headers) as response:
        content = await response.json()
        logging.info(f"{api_url}: {content}...")
    await session.close()
    return len(content)


async def startup(ctx: Dict) -> None:
    ctx["session"] = ClientSession()
    ctx["pool"] = ThreadPoolExecutor()


async def shutdown(ctx: Dict) -> None:
    await ctx["session"].close()


def gen_cron_jobs(interval: int) -> List:
    assert 10 <= interval < 3600
    if interval <= 60:
        RUN_TIMES = set(range(0, 60, interval))
        cron_jobs = [cron(update_task_status, second=RUN_TIMES)]  # type: ignore
    else:
        RUN_TIMES = set(range(0, 60, interval // 60))
        cron_jobs = [cron(update_task_status, minute=RUN_TIMES)]  # type: ignore
    return cron_jobs


class WorkerSettings:
    cron_jobs = gen_cron_jobs(CHECK_INTERVAL_IN_SECONDS)
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(REDIS_URI)
