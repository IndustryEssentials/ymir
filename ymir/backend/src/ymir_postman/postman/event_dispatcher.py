""" event dispatcher """

import logging
from typing import Callable

import redis

from postman.settings import constants, settings


# public: class EventDispatcher
class EventDispatcher:
    def __init__(self, event_name: str, handler: Callable) -> None:
        if not event_name:
            raise ValueError('empty event name')

        if not handler:
            raise ValueError('empty handler')

        self._event_handler = handler
        self._event_name = event_name
        self._group_name = f"group:{event_name}"
        self._redis_connect: redis.Redis = self.get_redis_connect()

        # creates stream and consumer group
        self.add_event(event_name=self._event_name, event_topic=constants.EVENT_TOPIC_INNER, event_body='')
        try:
            self._redis_connect.xgroup_create(name=self._event_name, groupname=self._group_name, id='$')
        except redis.ResponseError as e:
            logging.debug(f"xgroup_create: {e}")

    # public: general
    def start(self) -> None:
        """ start to listen """
        logging.debug(f"ed start. event: {self._event_name}, group: {self._group_name}")
        kvs = self._redis_connect.xreadgroup(groupname=self._group_name,
                                             consumername='default',
                                             streams={self._event_name: '0'})
        while True:
            for _, stream_msgs in kvs:
                if not stream_msgs:
                    continue

                self._event_handler(ed=self, mid_and_msgs=stream_msgs)

                msg_ids, *_ = zip(*stream_msgs)
                self._redis_connect.xack(self._event_name, self._group_name, *msg_ids)
                self._redis_connect.xdel(self._event_name, *msg_ids)

            kvs = self._redis_connect.xreadgroup(groupname=self._group_name,
                                                 consumername='default',
                                                 streams={self._event_name: '>'},
                                                 block=0)

    @classmethod
    def get_redis_connect(cls) -> redis.Redis:
        return redis.StrictRedis.from_url(settings.PM_REDIS_URI, encoding="utf8", decode_responses=True)

    @classmethod
    def add_event(cls, event_name: str, event_topic: str, event_body: str) -> None:
        cls.get_redis_connect().xadd(name=event_name,
                                     fields={
                                         'topic': event_topic,
                                         'body': event_body
                                     },
                                     maxlen=settings.MAX_REDIS_STREAM_LENGTH,
                                     approximate=True)
