import yaml

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


# Current ymir system version
YMIR_VERSION = '2.1.0'
YMIR_REPO_VERSION = '2.0.0'
YMIR_MODEL_VERSION = '2.0.0'

# Default sandbox version
DEFAULT_YMIR_SRC_VERSION = '1.1.0'

# Protocol version for training, mining and infer executors
TMI_PROTOCOL_VERSION = '1.1.0'


def ymir_salient_version(ver: str) -> str:
    """
    get sailent version of repo and model versions
    """
    if ver in {'2.0.0', '2.0.1', '2.0.2'}:
        return '2.0.0'
    return ver


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


def check_ymir_version_or_crash(ver: str) -> None:
    if ymir_salient_version(ver) != YMIR_REPO_VERSION:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"Version mismatch between: {ver} and {YMIR_REPO_VERSION}")


def check_model_version_or_crash(ver: str) -> None:
    if ymir_salient_version(ver) != YMIR_MODEL_VERSION:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MODEL_PACKAGE_VERSION,
                              error_message=f"Model package version mismatch between: {ver} and {YMIR_MODEL_VERSION}")
