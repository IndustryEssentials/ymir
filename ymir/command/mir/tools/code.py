from enum import IntEnum

from mir.protos import mir_command_pb2 as mirpb


class MirCode(IntEnum):
    # everything is ok, command finished without any errors or warnings
    RC_OK = mirpb.RC_OK

    # errors: command failed for some reasons
    RC_CMD_ERROR_UNKNOWN = mirpb.RCode.RC_CMD_ERROR_UNKNOWN  # unknown error(s) occured while command executed
    RC_CMD_INVALID_MIR_REPO = mirpb.RCode.RC_CMD_INVALID_MIR_REPO  # mir command not invoked inside a mir repo
    RC_CMD_INVALID_ARGS = mirpb.RCode.RC_CMD_INVALID_ARGS  # lack of necessary args, or unexpected args
    RC_CMD_INVALID_BRANCH_OR_TAG = mirpb.RCode.RC_CMD_INVALID_BRANCH_OR_TAG  # invalid branch name or tag name
    RC_CMD_INVALID_MIR_FILE = mirpb.RCode.RC_CMD_INVALID_MIR_FILE  # invalid mir files
    RC_CMD_INVALID_COMMAND = mirpb.RCode.RC_CMD_INVALID_COMMAND  # unknown command or sub command
    RC_CMD_MIR_FILE_NOT_FOUND = mirpb.RCode.RC_CMD_MIR_FILE_NOT_FOUND  # can not find some mir files
    RC_CMD_CONFLICTS_OCCURED = mirpb.RCode.RC_CMD_CONFLICTS_OCCURED  # conflicts detected when mir pull or mir merge
    RC_CMD_EMPTY_METADATAS = mirpb.RCode.RC_CMD_EMPTY_METADATAS  # no assets found in metadatas.mir
    RC_CMD_EMPTY_TRAIN_SET = mirpb.RCode.RC_CMD_EMPTY_TRAIN_SET  # no training set when training
    RC_CMD_EMPTY_VAL_SET = mirpb.RCode.RC_CMD_EMPTY_VAL_SET  # no validation set when training
    RC_CMD_DIRTY_REPO = mirpb.RCode.RC_CMD_DIRTY_REPO  # no validation set when training
    RC_CMD_NOTHING_TO_MERGE = mirpb.RCode.RC_CMD_NOTHING_TO_MERGE
    RC_RUNTIME_ERROR_UNKNOWN = mirpb.RCode.RC_RUNTIME_ERROR_UNKNOWN
    RC_RUNTIME_UNKNOWN_TYPES = mirpb.RCode.RC_RUNTIME_UNKNOWN_TYPES
    RC_RUNTIME_CONTAINER_ERROR = mirpb.RCode.RC_RUNTIME_CONTAINER_ERROR
