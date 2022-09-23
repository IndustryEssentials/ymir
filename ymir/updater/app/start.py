import logging
import os
import sys

from common_utils import sandbox_updater, sandbox_util
from mir.version import YMIR_VERSION


def main() -> int:
    sandbox_root = os.environ['BACKEND_SANDBOX_ROOT']

    sandbox_versions = sandbox_util.detect_sandbox_src_versions(sandbox_root)
    if len(sandbox_versions) != 1:
        raise Exception(f"invalid sandbox versions: {sandbox_versions}")

    sandbox_updater.update(sandbox_root=sandbox_root,
                           src_ver=sandbox_versions[0],
                           dst_ver=YMIR_VERSION)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    sys.exit(main())
