from enum import IntEnum

import yaml

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


# Current ymir system version
YMIR_VERSION = '2.0.1'

# Default sandbox version
DEFAULT_YMIR_SRC_VERSION = '1.1.0'

# Protocol version for training, mining and infer executors
TMI_PROTOCOL_VERSION = '1.1.0'


def ymir_salient_version(ver: str) -> str:
    _SALIENT_VERSIONS = {
        DEFAULT_YMIR_SRC_VERSION: DEFAULT_YMIR_SRC_VERSION,
        '1.3.0': '2.0.0',
        '2.0.0': '2.0.0',
        '2.0.1': '2.0.0',
    }
    return _SALIENT_VERSIONS[ver]


def ymir_salient_version_from_label_file(user_label_file: str) -> str:
    """
    parse salient version from labels.yaml

    Raises:
        FileNotFoundError if file not found
        yaml.YAMLError if yaml parse failed
    """
    with open(user_label_file, 'r') as f:
        user_label_dict = yaml.safe_load(f)
    return ymir_salient_version(user_label_dict.get('ymir_version', DEFAULT_YMIR_SRC_VERSION))


def ymir_model_salient_version(ver: str) -> str:
    """
    get model package version from ymir version
    """
    _PACKAGE_VERSIONS = {
        DEFAULT_YMIR_SRC_VERSION: DEFAULT_YMIR_SRC_VERSION,
        '1.3.0': '2.0.0',
        '2.0.0': '2.0.0',
        '2.0.1': '2.0.0',
    }
    return _PACKAGE_VERSIONS[ver]


class CheckVersionType(IntEnum):
    CVT_LABEL_VERSION = 1
    CVT_MODEL_VERSION = 2


def check_version_valid(ver: str,
                        type: CheckVersionType = CheckVersionType.CVT_LABEL_VERSION,
                        raise_if_mismatch: bool = True) -> bool:
    funcs_map = {
        CheckVersionType.CVT_LABEL_VERSION: ymir_salient_version,
        CheckVersionType.CVT_MODEL_VERSION: ymir_model_salient_version,
    }
    salient_ver_func = funcs_map[type]
    if salient_ver_func(ver) != salient_ver_func(YMIR_VERSION):
        if raise_if_mismatch:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"Version mismatch between {ver} and {YMIR_VERSION}")
        return False
    return True
