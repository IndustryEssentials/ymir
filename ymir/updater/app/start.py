import logging
import os
import sys

from common_utils import sandbox
from mir.version import YMIR_VERSION

import update_1_1_0_to_1_3_0.step_updater


def main() -> int:
    sandbox_root = os.environ['BACKEND_SANDBOX_ROOT']

    sandbox.update(sandbox_root=sandbox_root,
                   src_ver=sandbox.detect_sandbox_src_ver(sandbox_root),
                   dst_ver=YMIR_VERSION)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    sys.exit(main())