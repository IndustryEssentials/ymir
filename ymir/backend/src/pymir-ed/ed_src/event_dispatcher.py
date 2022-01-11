""" event dispatcher """

import logging
import multiprocessing
import os
from typing import Any, Callable, Set

import redis


# public: class EventDispatcher
class EventDispatcher:
    def __init__(self, event_name: str) -> None:
        self._event_handler: Callable = None
        self._event_name = event_name
        self._group_name = f"group:{event_name}"
        self._redis_connect = None
        self._process = None

    # public: lifecycle
    def start(self) -> None:
        # start redis listeners in another process
        self._process = multiprocessing.Process(target=EventDispatcher._start, args=(self, ))
        self._process.start()

    def wait(self) -> None:
        self._process.join()

    @classmethod
    def get_redis_connect(cls) -> redis.Redis:
        redis_uri = os.environ.get("ED_REDIS_URI", "redis://")
        return redis.StrictRedis.from_url(redis_uri, encoding="utf8", decode_responses=True)

    def register_handler(self, handler: Callable) -> None:
        if self._event_handler:
            logging.warning('event handler already registered')
            return
        self._event_handler = handler

    # public: producer
    def add_event(self, event_topic: str, event_body: str) -> None:
        result = self.get_redis_connect().xadd(name=self._event_name,
                                               fields={
                                                   'topic': event_topic,
                                                   'body': event_body
                                               },
                                               maxlen=17280000,
                                               approximate=True)
        logging.info(f"xadd: {result}")

    # private: start
    def _start(self) -> None:
        # connect to redis
        self._redis_connect = self.get_redis_connect()
        # create stream
        self._create_stream_if_necessary()
        # create group
        self._create_consumer_group_if_necessary()
        # listen to stream
        self._read_redis_stream_pending_msgs()
        self._read_redis_stream_new_msgs()

    # private: redis stream and consumer group
    def _stream_exists(self) -> bool:
        if not self._event_name:
            raise ValueError('empty event name')

        try:
            stream_info = self._redis_connect.xinfo_stream(self._event_name)
            return stream_info is not None
        except redis.exceptions.ResponseError as e:
            logging.error(e)
            return False

    def _consumer_group_exists(self) -> bool:
        if not self._event_name or not self._group_name:
            raise ValueError('empty event name or group name')

        try:
            groups_info = self._redis_connect.xinfo_groups(self._event_name)
            group_names: Set[str] = {group['name'] for group in groups_info}
            return self._group_name in group_names
        except redis.exceptions.ResponseError as e:
            logging.error(e)
            return False

    def _create_stream_if_necessary(self) -> None:
        if not self._stream_exists():
            # create redis stream by an empty message
            # there's no create stream command in redis
            self.add_event(event_topic='_inner_', event_body='')

    def _create_consumer_group_if_necessary(self) -> None:
        if not self._consumer_group_exists():
            self._redis_connect.xgroup_create(name=self._event_name, groupname=self._group_name, id='$')

    def _read_redis_stream_pending_msgs(self) -> None:
        kvs = self._redis_connect.xreadgroup(groupname=self._group_name,
                                             consumername='default',
                                             streams={self._event_name: '0'})
        for _, stream_msgs in kvs:
            if not stream_msgs:
                continue

            msg_ids, *_ = zip(*stream_msgs)
            self._handler_wrapper(stream_msgs)
            self._redis_connect.xack(self._event_name, self._group_name, *msg_ids)
            self._redis_connect.xdel(self._event_name, *msg_ids)

    def _read_redis_stream_new_msgs(self) -> Any:
        while True:
            kvs = self._redis_connect.xreadgroup(groupname=self._group_name,
                                                 consumername='default',
                                                 streams={self._event_name: '>'},
                                                 block=0)
            for _, stream_msgs in kvs:
                if not stream_msgs:
                    continue

                msg_ids, *_ = zip(*stream_msgs)
                self._handler_wrapper(stream_msgs)
                self._redis_connect.xack(self._event_name, self._group_name, *msg_ids)
                self._redis_connect.xdel(self._event_name, *msg_ids)

    # private: _handler_wrapper
    def _handler_wrapper(self, mid_and_msgs: list) -> None:
        if not self._event_handler:
            logging.warning('_handler_wrapper: empty event handler')
            return

        try:
            self._event_handler(ed=self, mid_and_msgs=mid_and_msgs)
        except BaseException:
            logging.exception(msg='error occured in handler: {self._event_handler.__name__}')
