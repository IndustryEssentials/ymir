# Package version
YMIR_VERSION = '1.3.0'
DEFAULT_YMIR_SRC_VERSION = '1.1.0'


def ymir_salient_version(ver: str) -> str:
    _SALIENT_VERSIONS = {
        DEFAULT_YMIR_SRC_VERSION: DEFAULT_YMIR_SRC_VERSION,
        '1.3.0': '1.3.0',
    }
    return _SALIENT_VERSIONS[ver]
