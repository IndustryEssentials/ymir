from enum import unique, IntEnum, Enum


@unique
class CeleryTaskStatus(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    RETRY = "RETRY"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@unique
class FiftyoneTaskStatus(IntEnum):
    PENDING = 1
    PROCESSING = 2
    READY = 3
    OBSOLETE = 4
    ERROR = 5
