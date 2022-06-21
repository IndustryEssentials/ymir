from enum import unique, IntEnum, Enum


@unique
class CeleryTaskStatus(Enum):
    PENDING = "pending"
    STARTED = "started"
    RETRY = "retry"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILURE = "failure"


@unique
class FiftyoneTaskStatus(IntEnum):
    PENDING = 1
    PROCESSING = 2
    READY = 3
    OBSOLETE = 4
    ERROR = 5
