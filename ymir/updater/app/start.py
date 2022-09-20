import logging
import os
import sys
from types import ModuleType
from typing import Dict, Tuple

from common_utils import sandbox
from mir.version import YMIR_VERSION

import update_1_1_0_to_1_3_0.step_updater


class UpdateError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__()
        self.code = code
        self.message = message


def _get_update_steps(src_ver: str) -> Tuple[ModuleType, ...]:
    _UPDATE_STEPS: Dict[Tuple[str, str], Tuple[ModuleType, ...]] = {
        ('1.1.0', '1.3.0'): (update_1_1_0_to_1_3_0.step_updater, ),
    }
    return _UPDATE_STEPS.get((src_ver, YMIR_VERSION))


def main() -> int:
    if os.environ['EXPECTED_YMIR_VERSION'] != YMIR_VERSION:
        raise Exception('.env version not matched')

    sandbox_root = os.environ['BACKEND_SANDBOX_ROOT']
    src_ver = sandbox.detect_sandbox_src_ver(sandbox_root)
    update_step_modules = _get_update_steps(src_ver)
    if not update_step_modules:
        raise Exception(f"Sandbox version: {src_ver} not supported")

    update_funcs = [getattr(update_module, 'update_all') for update_module in update_step_modules]
    sandbox.update(sandbox_root=sandbox_root, update_funcs=update_funcs)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    sys.exit(main())
