""" event dispatcher """

import multiprocessing
import os
import traceback
from typing import Any, Callable, Set

import redis


# public: class EventDispatcher
class EventDispatcher:
    def __init__(self, event_name: str) -> None:
        self._event_handler: Callable = None
        self._event_name = event_name
        self._group_name = f"group:{event_name}"
        self._redis_connect = None
        self._redis_producer_connect = None

    # public: lifecycle
    def start(self) -> None:
        if self._redis_producer_connect:
            print('event dispatcher already started')
            return

        redis_uri = os.environ.get("ED_REDIS_URI", "redis://")
        self._redis_producer_connect = redis.StrictRedis.from_url(redis_uri, encoding="utf8", decode_responses=True)

        # start redis listeners in another thread
        p = multiprocessing.Process(target=EventDispatcher._start, args=(self, ))
        p.start()

    def register_handler(self, handler: Callable) -> None:
        if self._event_handler:
            print('event handler already registered')
            return
        self._event_handler = handler

    # public: producer
    def add_event(self, event_topic: str, event_body: str) -> None:
        self._redis_producer_connect.xadd(name=self._event_name,
                                          fields={
                                              'topic': event_topic,
                                              'body': event_body
                                          },
                                          maxlen=17280000,
                                          approximate=True)

    # private: start
    def _start(self) -> None:
        redis_uri = os.environ.get("ED_REDIS_URI", "redis://")
        # connect to redis
        self._redis_connect = redis.StrictRedis.from_url(redis_uri, encoding="utf8", decode_responses=True)
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

        stream_info = self._redis_connect.xinfo_stream(self._event_name)
        return stream_info is not None

    def _consumer_group_exists(self) -> bool:
        if not self._event_name or not self._group_name:
            raise ValueError('empty event name or group name')

        groups_info = self._redis_connect.xinfo_groups(self._event_name)
        group_names: Set[str] = {group['name'] for group in groups_info}
        return self._group_name in group_names

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

            # TODO: HANDLE DEADLETTER
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

                # TODO: HANDLE DEADLETTER
                msg_ids, *_ = zip(*stream_msgs)
                self._handler_wrapper(stream_msgs)
                self._redis_connect.xack(self._event_name, self._group_name, *msg_ids)
                self._redis_connect.xdel(self._event_name, *msg_ids)

    # private: _handler_wrapper
    def _handler_wrapper(self, mid_and_msgs: list) -> None:
        if not self._event_handler:
            return

        try:
            self._event_handler(ed=self, mid_and_msgs=mid_and_msgs)
        except BaseException as e:
            print(f"error occured in handler: {self._event_handler.__name__}: {e}")
            traceback.print_exc()
