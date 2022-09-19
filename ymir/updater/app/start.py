import logging
import os
import shutil
import sys
from types import ModuleType
from typing import Callable, Dict, Set, Tuple

import errors as update_errors
from common_utils import sandbox
from mir.version import YMIR_VERSION

import update_1_1_0_to_1_3_0.step_updater



def _get_update_steps(src_ver: str) -> Tuple[ModuleType, ...]:
    _UPDATE_STEPS: Dict[Tuple[str, str], Tuple[ModuleType, ...]] = {
        ('1.1.0', '1.3.0'): (update_1_1_0_to_1_3_0.step_updater, ),
    }
    return _UPDATE_STEPS.get((src_ver, YMIR_VERSION), None)


def _exc_update_steps(update_steps: Tuple[ModuleType, ...], sandbox_root: str) -> None:
    for step_module in update_steps:
        step_func: Callable = getattr(step_module, 'update_all')
        step_func(sandbox_root)


def main() -> int:
    if os.environ['EXPECTED_YMIR_VERSION'] != YMIR_VERSION:
        raise update_errors.EnvVersionNotMatch()

    sandbox_root = os.environ['BACKEND_SANDBOX_ROOT']
    src_ver = sandbox.detect_sandbox_src_ver(sandbox_root)
    update_steps = _get_update_steps(src_ver)
    if not update_steps:
        raise update_errors.SandboxVersionNotSupported(sandbox_version=src_ver)

    sandbox.backup(sandbox_root)
    try:
        _exc_update_steps(update_steps=update_steps, sandbox_root=sandbox_root)
    except Exception as e:
        sandbox.roll_back(sandbox_root)
        raise e

    # cleanup
    sandbox.remove_backup(sandbox_root)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    sys.exit(main())
