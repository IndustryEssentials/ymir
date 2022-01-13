""" event dispatcher """

import logging
from typing import Any, Callable, Set

import redis

from postman.settings import settings


# public: class EventDispatcher
class EventDispatcher:
    def __init__(self, event_name: str) -> None:
        if not event_name:
            raise ValueError('empty event name')

        self._event_handler: Any = None
        self._event_name = event_name
        self._group_name = f"group:{event_name}"
        self._redis_connect: redis.Redis = self.get_redis_connect()
        self._config_stream_and_group()

    # public: general
    def start(self) -> None:
        # listen to stream
        logging.debug('start listening')
        self._read_redis_stream_pending_msgs()
        self._read_redis_stream_new_msgs()

    @classmethod
    def get_redis_connect(cls) -> redis.Redis:
        return redis.StrictRedis.from_url(settings.PM_REDIS_URI, encoding="utf8", decode_responses=True)

    def register_handler(self, handler: Callable) -> None:
        self._event_handler = handler

    @classmethod
    def add_event(cls, event_name: str, event_topic: str, event_body: str) -> None:
        cls.get_redis_connect().xadd(name=event_name,
                                     fields={
                                         'topic': event_topic,
                                         'body': event_body
                                     },
                                     maxlen=settings.MAX_REDIS_STREAM_LENGTH,
                                     approximate=True)

    # private: redis stream and consumer group
    def _stream_exists(self) -> bool:
        try:
            stream_info = self._redis_connect.xinfo_stream(self._event_name)
            return stream_info is not None
        except redis.exceptions.ResponseError as e:
            logging.error(e)
            return False

    def _consumer_group_exists(self) -> bool:
        try:
            groups_info = self._redis_connect.xinfo_groups(self._event_name)
            group_names: Set[str] = {group['name'] for group in groups_info}
            return self._group_name in group_names
        except redis.exceptions.ResponseError as e:
            logging.error(e)
            return False

    def _config_stream_and_group(self) -> None:
        if not self._stream_exists():
            # create redis stream by an empty message
            # there's no "create stream" command in redis
            self.add_event(event_name=self._event_name, event_topic='_inner_', event_body='')
        if not self._consumer_group_exists():
            self._redis_connect.xgroup_create(name=self._event_name, groupname=self._group_name, id='$')

    def _read_redis_stream_pending_msgs(self) -> None:
        kvs = self._redis_connect.xreadgroup(groupname=self._group_name,
                                             consumername='default',
                                             streams={self._event_name: '0'})
        self._handle_msgs_and_remove(kvs)

    def _read_redis_stream_new_msgs(self) -> Any:
        while True:
            kvs = self._redis_connect.xreadgroup(groupname=self._group_name,
                                                 consumername='default',
                                                 streams={self._event_name: '>'},
                                                 block=0)
            self._handle_msgs_and_remove(kvs)

    def _handle_msgs_and_remove(self, kvs: Any) -> None:
        if not self._event_handler:
            logging.warning('EventDispatcher: handler not set')
            return

        for _, stream_msgs in kvs:
            if not stream_msgs:
                continue

            try:
                self._event_handler(ed=self, mid_and_msgs=stream_msgs)
            except BaseException:
                logging.exception(msg='error occured in handler: {self._event_handler.__name__}')

            msg_ids, *_ = zip(*stream_msgs)
            self._redis_connect.xack(self._event_name, self._group_name, *msg_ids)
            self._redis_connect.xdel(self._event_name, *msg_ids)
