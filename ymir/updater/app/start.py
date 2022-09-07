import os
import sys
from typing import List, Set
from version import YMIR_VERSION


def _get_from_version(sandbox_dir: str) -> str:
    pass


def _get_update_steps(from_version: str, to_version: str) -> List[str]:
    pass


def _exc_update_steps(update_steps: List[str]) -> None:
    pass


def _backup() -> None:
    pass


def main() -> int:
    print(f'ymir updater for version: {YMIR_VERSION}')

    sandbox_dir = os.environ['BACKEND_SANDBOX_ROOT']
    from_version = _get_from_version(sandbox_dir)

    update_steps = _get_update_steps(from_version=from_version, to_version=YMIR_VERSION)
    if not update_steps:
        return 0

    _backup()
    _exc_update_steps(update_steps)
    return 0


if __name__ == '__main__':
    sys.exit(main())
