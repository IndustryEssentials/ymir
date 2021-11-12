from enum import IntEnum, unique

from ymir.protos import mir_common_pb2 as mir_common


@unique
class ResCode(IntEnum):
    # everything is ok, command finished without any errors or warnings
    CTR_OK = mir_common.RCode.RC_OK

    # errors: command failed for some reasons
    CTR_ERROR_UNKNOWN = mir_common.RCode.RC_SERVICE_ERROR_UNKNOWN  # unknown error(s) occured while command executed
    CTR_INVALID_SERVICE_REQ = mir_common.RCode.RC_SERVICE_INVALID_REQ
    CTR_SERVICE_INVOKE_ERROR = mir_common.RCode.RC_SERVICE_INVOKE_ERROR
    CTR_SERVICE_UNKOWN_RESPONSE = mir_common.RCode.RC_SERVICE_UNKOWN_RESPONSE
    CTR_SERVICE_TASK_INVOKER_ERROR = mir_common.RCode.RC_SERVICE_TASK_INVOKER_ERROR
    CTR_SERVICE_INFO_INVOKER_ERROR = mir_common.RCode.RC_SERVICE_INFO_INVOKER_ERROR
