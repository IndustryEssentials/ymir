# Current ymir system version
YMIR_VERSION = '2.0.0'

# Default sandbox version
DEFAULT_YMIR_SRC_VERSION = '1.1.0'

# Protocol version for training, mining and infer executors
TMI_PROTOCOL_VERSION = '1.1.0'


def ymir_salient_version(ver: str) -> str:
    _SALIENT_VERSIONS = {
        DEFAULT_YMIR_SRC_VERSION: DEFAULT_YMIR_SRC_VERSION,
        '1.3.0': '2.0.0',
        '2.0.0': '2.0.0',
    }
    return _SALIENT_VERSIONS[ver]


def ymir_model_salient_version(ver: str) -> str:
    """
    get model package version from ymir version
    """
    _PACKAGE_VERSIONS = {
        DEFAULT_YMIR_SRC_VERSION: DEFAULT_YMIR_SRC_VERSION,
        '1.3.0': '2.0.0',
        '2.0.0': '2.0.0',
    }
    return _PACKAGE_VERSIONS[ver]
