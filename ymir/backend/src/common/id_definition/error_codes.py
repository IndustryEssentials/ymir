from enum import IntEnum, unique


@unique
class CMDResponseCode(IntEnum):
    """
    duplicated from `mir.tools.code.MirCode`
    """

    RC_OK = 0  # everything is ok, command finished without any errors or warnings
    RC_CMD_INVALID_ARGS = 160001  # lack of necessary args, or unexpected args
    RC_CMD_EMPTY_TRAIN_SET = 160002  # no training set when training
    RC_CMD_EMPTY_VAL_SET = 160003  # no validation set when training
    RC_CMD_CONTAINER_ERROR = 160004  # container errors
    RC_CMD_UNKNOWN_TYPES = 160005  # unknown types found, and can not be ignored when mir import
    RC_CMD_INVALID_BRANCH_OR_TAG = 160006  # invalid branch name or tag name
    RC_CMD_DIRTY_REPO = 160007  # repo is dirty when mir commit
    RC_CMD_MERGE_ERROR = 160008  # error occured when mir merge
    RC_CMD_INVALID_MIR_REPO = 160009
    RC_CMD_INVALID_FILE = 160010
    RC_CMD_NO_RESULT = 160011  # no result for training, mining and infer
    RC_CMD_OPENPAI_ERROR = 160012
    RC_CMD_NO_ANNOTATIONS = 160013
    RC_CMD_CAN_NOT_CALC_CONFUSION_MATRIX = 160014
    RC_CMD_INVALID_MODEL_PACKAGE_VERSION = 160015
    RC_CMD_INVALID_META_YAML_FILE = 160016
    RC_CMD_ERROR_UNKNOWN = 169999


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
    INVOKER_HTTP_ERROR = 130604
    INVOKER_UNKNOWN_ERROR = 130605
    INVOKER_INVALID_ARGS = 130606
    INVOKER_INVALID_ASSETS = 130607


@unique
class VizErrorCode(IntEnum):
    GENERAL_ERROR = 140400
    BRANCH_NOT_EXISTS = 140401
    MODEL_NOT_EXISTS = 140402
    DATASET_EVALUATION_NOT_EXISTS = 140403
    NO_CLASS_IDS = 140404
    INVALID_ANNO_TYPE = 140405
    INTERNAL_ERROR = 140500
    TOO_MANY_DATASETS_TO_CHECK = 140600


@unique
class MonitorErrorCode(IntEnum):
    GENERAL_ERROR = 150400
    DUPLICATE_TASK_ID = 150401
    PERCENT_LOG_FILE_ERROR = 150402
    PERCENT_LOG_WEIGHT_ERROR = 150403
    PERCENT_LOG_PARSE_ERROR = 150404
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
    FAILED_TO_PROCESS_PROTECTED_RESOURCES = 110111
    SYSTEM_VERSION_CONFLICT = 110112
    FAILED_TO_SEND_EMAIL = 110113

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
    DATASET_PROTECTED_TO_DELETE = 110405
    DATASETS_NOT_IN_SAME_GROUP = 110406
    INVALID_DATASET_STRUCTURE = 110407
    DATASET_FAILED_TO_IMPORT = 110408
    INVALID_DATASET_ZIP_FILE = 110409
    DATASET_INDEX_NOT_READY = 110410

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
    INVALID_PROJECT = 111404

    DATASET_GROUP_NOT_FOUND = 111501
    DATASET_GROUP_DUPLICATED_NAME = 111502
    DATASET_GROUP_FAILED_TO_CREATE = 111503

    MODEL_GROUP_NOT_FOUND = 111601
    MODEL_GROUP_DUPLICATED_NAME = 111602
    MODEL_GROUP_FAILED_TO_CREATE = 111603

    ITERATION_NOT_FOUND = 111701
    ITERATION_FAILED_TO_CREATE = 111703
    ITERATION_COULD_NOT_UPDATE_STAGE = 111704
    ITERATION_STEP_NOT_FOUND = 111705
    ITERATION_STEP_ALREADY_FINISHED = 111706
    ITERATION_DUPLICATED = 111707

    FAILED_TO_IMPORT_MODEL = 111801

    REFUSE_TO_PROCESS_MIXED_OPERATIONS = 111901
    FAILED_TO_EVALUATE = 111902
    DATASET_EVALUATION_NOT_FOUND = 111903
    MISSING_OPERATIONS = 111904
    DATASET_EVALUATION_NO_ANNOTATIONS = 111905
    PREMATURE_DATASETS = 111906

    MODEL_STAGE_NOT_FOUND = 112001
    INVALID_MODEL_STAGE_NAME = 112002

    VIZ_ERROR = 112101
    FAILED_TO_PARSE_VIZ_RESP = 112102
    VIZ_TIMEOUT = 112103

    VISUALIZATION_NOT_FOUND = 112201


class UpdaterErrorCode(IntEnum):
    INVALID_USER_LABEL_FILE = 170001
    SANDBOX_VERSION_NOT_SUPPORTED = 170002
