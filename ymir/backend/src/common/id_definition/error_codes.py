from enum import IntEnum, unique


@unique
class CTLResponseCode(IntEnum):
    CTR_OK = 0

    ARG_VALIDATION_FAILED = 130400
    DOCKER_IMAGE_ERROR = 130401
    RUN_COMMAND_ERROR = 130402
    INTERNAL_ERROR = 130500
    UNKOWN_RESPONSE_FORMAT = 130501
    MIS_MATCHED_INVOKER_TYPE = 130502
    REG_LOG_MONITOR_ERROR = 130503
    LOCK_GPU_ERROR = 130504
    INVOKER_GENERAL_ERROR = 130600
    INVOKER_INIT_ERROR = 130601
    INVOKER_LABEL_TASK_UNKNOWN_ERROR = 130602
    INVOKER_LABEL_TASK_NETWORK_ERROR = 130603


@unique
class VizErrorCode(IntEnum):
    GENERAL_ERROR = 140400
    BRANCH_NOT_EXISTS = 140401
    MODEL_NOT_EXISTS = 140402
    INTERNAL_ERROR = 140500


@unique
class MonitorErrorCode(IntEnum):
    GENERAL_ERROR = 150400
    DUPLICATE_TASK_ID = 150401
    PERCENT_LOG_FILE_ERROR = 150402
    PERCENT_LOG_WEIGHT_ERROR = 150403
    INTERNAL_ERROR = 150500


@unique
class APIErrorCode(IntEnum):
    API_ERROR = 110101
    VALIDATION_FAILED = 110102
    UNKNOWN_ERROR = 110103
    INVALID_TOKEN = 110104
    REQUIRED_FIELD_MISSING = 110105
    CONTROLLER_ERROR = 110106
    INCORRECT_EMAIL_OR_PASSWORD = 110107
    FAILED_TO_DOWNLOAD = 110108
    INVALID_CONFIGURATION = 110109
    INVALID_SCOPE = 110110

    USER_NOT_FOUND = 110201
    USER_DUPLICATED_NAME = 110202
    USER_NOT_ACCESSIBLE = 110203
    USER_NOT_LOGGED_IN = 110204
    USER_NOT_ADMIN = 110205
    USER_NOT_ACTIVE = 110206
    USER_ROLE_NOT_ELIGIBLE = 110207
    USER_FAILED_TO_CREATE = 110208

    DATASET_NOT_FOUND = 110401
    DATASET_DUPLICATED_NAME = 110402
    DATASET_NOT_ACCESSIBLE = 110403
    DATASET_FAILED_TO_CREATE = 110404

    ASSET_NOT_FOUND = 110501

    MODEL_NOT_FOUND = 110601
    MODEL_DUPLICATED_NAME = 110602
    MODEL_NOT_ACCESSIBLE = 110603
    MODEL_FAILED_TO_CREATE = 110604
    MODEL_NOT_READY = 110605

    TASK_NOT_FOUND = 110701
    TASK_DUPLICATED_NAME = 110702
    TASK_NOT_ACCESSIBLE = 110703
    TASK_FAILED_TO_CREATE = 110704
    TASK_STATUS_OBSOLETE = 110705
    FAILED_TO_UPDATE_TASK_STATUS = 110706

    GRAPH_NOT_FOUND = 110801

    INFERENCE_FAILED_TO_CALL = 110901
    INFERENCE_CONFIG_ERROR = 110902

    KEYWORD_DUPLICATED = 111001

    DOCKER_IMAGE_DUPLICATED = 111101
    DOCKER_IMAGE_NOT_FOUND = 111102
    FAILED_TO_SHARE_DOCKER_IMAGE = 111103
    DOCKER_IMAGE_HAVING_RELATIONSHIPS = 111104
    FAILED_TO_GET_SHARED_DOCKER_IMAGES = 111105
    SHARED_IMAGE_CONFIG_ERROR = 111106

    FAILED_TO_GET_SYS_INFO = 111201

    FAILED_TO_CONNECT_CLICKHOUSE = 111301

    PROJECT_NOT_FOUND = 111401
    PROJECT_DUPLICATED_NAME = 111402
    PROJECT_FAILED_TO_CREATE = 111403

    DATASET_GROUP_NOT_FOUND = 111501
    DATASET_GROUP_DUPLICATED_NAME = 111502
    DATASET_GROUP_FAILED_TO_CREATE = 111503

    MODEL_GROUP_NOT_FOUND = 111601
    MODEL_GROUP_DUPLICATED_NAME = 111602
    MODEL_GROUP_FAILED_TO_CREATE = 111603

    ITERATION_NOT_FOUND = 111701
    ITERATION_FAILED_TO_CREATE = 111703
