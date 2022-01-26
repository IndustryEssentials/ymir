from enum import IntEnum


class MirCode(IntEnum):
    # TODO: REMOVE OLD
    # errors: command failed for some reasons
    # RC_CMD_ERROR_UNKNOWN = mirpb.RCode.RC_CMD_ERROR_UNKNOWN  # unknown error(s) occured while command executed
    # RC_CMD_INVALID_MIR_FILE = mirpb.RCode.RC_CMD_INVALID_MIR_FILE  # invalid mir files
    # RC_CMD_INVALID_COMMAND = mirpb.RCode.RC_CMD_INVALID_COMMAND  # unknown command or sub command
    # RC_CMD_MIR_FILE_NOT_FOUND = mirpb.RCode.RC_CMD_MIR_FILE_NOT_FOUND  # can not find some mir files
    # RC_CMD_CONFLICTS_OCCURED = mirpb.RCode.RC_CMD_CONFLICTS_OCCURED  # conflicts detected when mir pull or mir merge
    # RC_CMD_EMPTY_METADATAS = mirpb.RCode.RC_CMD_EMPTY_METADATAS  # no assets found in metadatas.mir
    # RC_CMD_NOTHING_TO_MERGE = mirpb.RCode.RC_CMD_NOTHING_TO_MERGE
    # RC_RUNTIME_ERROR_UNKNOWN = mirpb.RCode.RC_RUNTIME_ERROR_UNKNOWN

    RC_OK = 0  # everything is ok, command finished without any errors or warnings
    RC_CMD_INIT_ERROR = 233
    RC_CMD_INVALID_ARGS = 160001  # lack of necessary args, or unexpected args
    RC_CMD_EMPTY_TRAIN_SET = 160002  # no training set when training
    RC_CMD_EMPTY_VAL_SET = 160003  # no validation set when training
    RC_RUNTIME_CONTAINER_ERROR = 160004  # container errors
    RC_RUNTIME_UNKNOWN_TYPES = 160005  # unknown types found, and can not be ignored when mir import
    RC_CMD_INVALID_BRANCH_OR_TAG = 160006  # invalid branch name or tag name
    RC_CMD_DIRTY_REPO = 160007  # repo is dirty when mir commit
    RC_CMD_MERGE_ERROR = 160008  # error occured when mir merge
    RC_CMD_INVALID_MIR_REPO = 160009
