from enum import IntEnum
from functools import wraps
import logging
import time
from typing import Dict, Callable


class MirCode(IntEnum):
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
    RC_CMD_INVALID_OBJECT_TYPE = 160017
    RC_CMD_ERROR_UNKNOWN = 169999


def time_it(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: Dict) -> Callable:
        _start = time.time()
        _ret = f(*args, **kwargs)
        _cost = time.time() - _start
        logging.info(f"|-{f.__name__} costs {_cost:.2f}s({_cost / 60:.2f}m).")
        return _ret

    return wrapper
