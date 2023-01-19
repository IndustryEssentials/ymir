import logging
import os
import sys

from common_utils.sandbox_updater import update
from common_utils.sandbox_util import detect_sandbox_src_versions
from mir.version import YMIR_REPO_VERSION


def main() -> int:
    sandbox_root = os.environ['BACKEND_SANDBOX_ROOT']

    sandbox_versions = detect_sandbox_src_versions(sandbox_root)
    if len(sandbox_versions) != 1:
        raise Exception(f"invalid sandbox versions: {sandbox_versions}")

    update(sandbox_root=sandbox_root,
           assets_root=os.environ['ASSETS_PATH'],
           models_root=os.environ['MODELS_PATH'],
           src_ver=sandbox_versions[0],
           dst_ver=YMIR_REPO_VERSION)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='[%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.INFO)
    sys.exit(main())
