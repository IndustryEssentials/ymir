from enum import IntEnum, unique


@unique
class FiftyOneResponseCode(IntEnum):
    FO_OK = 0
    TASK_CREATE_ERROR = 1001
    TASK_PROCESS_ERROR = 1002
    TASK_NOT_FOUND = 1003
    FIFTYONE_SYSTEM_ERROR = 1004
    TASK_ALREADY_EXISTS = 1005
    REQUEST_VALIDATION_ERROR = 1010
