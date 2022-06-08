from enum import unique, IntEnum, Enum


@unique
class DataSetResultTypes(IntEnum):
    GROUND_TRUTH = 0  # ground_truth
    PREDICTION = 1  # prediction


@unique
class CeleryTaskStatus(Enum):
    PENDING = "penging"
    STARTED = "started"
    RETRY = "retry"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILURE = "failure"


@unique
class FiftyoneTaskStatus(Enum):
    PENDING = "penging"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    OBSOLETE = "obsolete"
