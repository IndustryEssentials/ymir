import logging
import os
import sys

from common_utils import sandbox_updater, sandbox_util
from mir.version import YMIR_VERSION


def main() -> int:
    sandbox_root = os.environ['BACKEND_SANDBOX_ROOT']

    sandbox_updater.update(sandbox_root=sandbox_root,
                           src_ver=sandbox_util.detect_sandbox_src_ver(sandbox_root),
                           dst_ver=YMIR_VERSION)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    sys.exit(main())
