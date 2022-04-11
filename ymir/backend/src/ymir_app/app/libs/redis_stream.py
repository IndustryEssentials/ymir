from typing import Any, Callable

import aioredis
from fastapi.logger import logger


class RedisStream:
    def __init__(
        self,
        redis_uri: str,
        stream_name: str = "ymir_app_stream",
        group_name: str = "ymir_app_group",
        consumer_name: str = "ymir_app_consumer",
    ):
        self.redis_uri = redis_uri
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name

    async def init_group_and_stream(self) -> None:
        await self.connect()
        exists = await self._conn.exists(self.stream_name)
        if not exists:
            logger.info("init redis stream and consumer group")
            await self._conn.xgroup_create(name=self.stream_name, groupname=self.group_name, mkstream=True)

    async def connect(self) -> None:
        self._conn = await aioredis.from_url(self.redis_uri, decode_responses=True)

    async def disconnect(self) -> None:
        await self._conn.close()

    async def publish(self, msg: Any) -> None:
        await self.connect()
        await self._conn.xadd(self.stream_name, {"payload": msg})
        logger.info("[redis stream] enqueue %s", msg)

    async def consume(self, f_processor: Callable) -> None:
        await self.init_group_and_stream()
        last_id = "0"
        check_backlog = True
        while True:
            # Pick the ID based on the iteration: the first time we want to
            # read our pending messages, in case we crashed and are recovering.
            # Once we consumed our history, we can start getting new messages.
            id_ = last_id if check_backlog else ">"
            for _, payloads in await self._conn.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={self.stream_name: id_},
                block=0,
            ):
                if not payloads:
                    # If we receive an empty reply, it means we were consuming our history
                    # and that the history is now empty. Let's start to consume new messages.
                    logger.info("handled all the legacy msgs")
                    check_backlog = False
                    continue
                logger.info("handling payloads %s", payloads)
                successful_ids = await f_processor(payloads)
                if successful_ids:
                    await self._conn.xack(self.stream_name, self.group_name, *successful_ids)
                last_id = payloads[-1][0]
