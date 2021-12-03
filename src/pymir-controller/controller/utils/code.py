from enum import IntEnum, unique

from proto import backend_pb2


@unique
class ResCode(IntEnum):
    # everything is ok, command finished without any errors or warnings
    CTR_OK = backend_pb2.RCode.RC_OK

    # errors: command failed for some reasons
    CTR_ERROR_UNKNOWN = backend_pb2.RCode.RC_SERVICE_ERROR_UNKNOWN  # unknown error(s) occured while command executed
    CTR_INVALID_SERVICE_REQ = backend_pb2.RCode.RC_SERVICE_INVALID_REQ
    CTR_SERVICE_INVOKE_ERROR = backend_pb2.RCode.RC_SERVICE_INVOKE_ERROR
    CTR_SERVICE_UNKOWN_RESPONSE = backend_pb2.RCode.RC_SERVICE_UNKOWN_RESPONSE
    CTR_SERVICE_TASK_INVOKER_ERROR = backend_pb2.RCode.RC_SERVICE_TASK_INVOKER_ERROR
    CTR_SERVICE_INFO_INVOKER_ERROR = backend_pb2.RCode.RC_SERVICE_INFO_INVOKER_ERROR
