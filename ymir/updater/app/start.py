import logging
import os
import shutil
import sys
from types import ModuleType
from typing import Any, Callable, Dict, Set, Tuple

import errors as update_errors
from common_utils.sandbox import SandboxInfo
from common_utils.version import YMIR_VERSION

import update_1_1_0_to_1_3_0.step_updater


_UPDATE_STEPS: Dict[Tuple[str, str], Tuple[ModuleType, ...]] = {
    ('1.1.0', '1.3.0'): (update_1_1_0_to_1_3_0.step_updater, ),
}


def _exc_update_steps(update_steps: Tuple[ModuleType, ...], sandbox_info: SandboxInfo) -> None:
    for step_module in update_steps:
        step_func: Callable = getattr(step_module, 'update_all')
        step_func(sandbox_info)


def _backup(sandbox_info: SandboxInfo) -> str:
    backup_dir = os.path.join(sandbox_info.root, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    if os.listdir(backup_dir):
        raise update_errors.BackupDirNotEmpty()

    for user_id, repo_ids in sandbox_info.user_to_repos.items():
        src_user_dir = os.path.join(sandbox_info.root, user_id)
        dst_user_dir = os.path.join(backup_dir, user_id)
        _copy_user_space(src_user_dir=src_user_dir, dst_user_dir=dst_user_dir, repo_ids=repo_ids)

    return backup_dir


def _roll_back(backup_dir: str, sandbox_info: SandboxInfo) -> None:
    for user_id, repo_ids in sandbox_info.user_to_repos.items():
        src_user_dir = os.path.join(backup_dir, user_id)
        dst_user_dir = os.path.join(sandbox_info.root, user_id)
        shutil.rmtree(dst_user_dir)
        _copy_user_space(src_user_dir=src_user_dir, dst_user_dir=dst_user_dir, repo_ids=repo_ids)


def _copy_user_space(src_user_dir: str, dst_user_dir: str, repo_ids: Set[str]) -> None:
    os.makedirs(dst_user_dir, exist_ok=True)
    shutil.copy(src=os.path.join(src_user_dir, 'labels.yaml'), dst=os.path.join(dst_user_dir, 'labels.yaml'))
    for repo_id in repo_ids:
        shutil.copytree(src=os.path.join(src_user_dir, repo_id), dst=os.path.join(dst_user_dir, repo_id))


def main() -> int:
    sandbox_info = SandboxInfo(root=os.environ['BACKEND_SANDBOX_ROOT'])
    if not sandbox_info.user_to_repos:
        logging.info('no need to update: found no users')
        return 0

    update_steps = _UPDATE_STEPS.get((sandbox_info.src_ver, YMIR_VERSION), None)
    if not update_steps:
        raise update_errors.SandboxVersionNotSupported(sandbox_version=sandbox_info.src_ver)

    backup_dir = _backup(sandbox_info)
    try:
        _exc_update_steps(update_steps=update_steps, sandbox_info=sandbox_info)
    except Exception as e:
        _roll_back(backup_dir=backup_dir, sandbox_info=sandbox_info)
        raise e

    # cleanup
    shutil.rmtree(backup_dir)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    sys.exit(main())
