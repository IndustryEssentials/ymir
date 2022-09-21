import logging
import os
import shutil
from typing import Callable, List

from common_utils.sandbox_util import detect_users_and_repos, SandboxError
from id_definition.error_codes import UpdaterErrorCode
from mir.version import DEFAULT_YMIR_SRC_VERSION

import update_1_1_0_to_1_3_0.step_updater


def update(sandbox_root: str, src_ver: str, dst_ver: str) -> None:
    steps = _get_update_steps(src_ver=src_ver, dst_ver=dst_ver)
    if not steps:
        raise SandboxError(error_code=UpdaterErrorCode.SANDBOX_VERSION_NOT_SUPPORTED,
                           error_message=f"Sandbox version: {src_ver} not supported")

    _backup(sandbox_root)

    # update
    user_to_repos = detect_users_and_repos(sandbox_root)
    try:
        for update_func in steps:
            for user_id, repo_ids in user_to_repos.items():
                for repo_id in repo_ids:
                    update_func(mir_root=os.path.join(sandbox_root, user_id, repo_id))
    except Exception as e:
        _roll_back(sandbox_root)
        raise e

    # cleanup
    shutil.rmtree(os.path.join(sandbox_root, 'backup'))


def _backup(sandbox_root: str) -> None:
    backup_dir = os.path.join(sandbox_root, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    if os.listdir(backup_dir):
        raise SandboxError(error_code=UpdaterErrorCode.BACKUP_DIR_NOT_EMPTY,
                           error_message=f"Backup directory not empty: {backup_dir}")

    for user_id in detect_users_and_repos(sandbox_root):
        shutil.copytree(src=os.path.join(sandbox_root, user_id), dst=os.path.join(backup_dir, user_id))


def _roll_back(sandbox_root: str) -> None:
    backup_dir = os.path.join(sandbox_root, 'backup')
    for user_id in detect_users_and_repos(sandbox_root):
        src_user_dir = os.path.join(backup_dir, user_id)
        dst_user_dir = os.path.join(sandbox_root, user_id)
        shutil.rmtree(dst_user_dir)
        shutil.copytree(src_user_dir, dst_user_dir)

    shutil.rmtree(os.path.join(sandbox_root, 'backup'))

    logging.info('roll back done')


def _get_equivalent_version(ver: str, default_ver: str = '') -> str:
    _EQUIVALENT_VERSIONS = {
        '1.1.0': '1.1.0',
        '1.3.0': '1.3.0',
    }
    return _EQUIVALENT_VERSIONS.get(ver, default_ver)


def _get_update_steps(src_ver: str, dst_ver: str) -> List[Callable[[str], None]]:
    eq_src_ver = _get_equivalent_version(src_ver, default_ver=DEFAULT_YMIR_SRC_VERSION)
    eq_dst_ver = _get_equivalent_version(dst_ver)

    _UPDATE_NODES = ['1.1.0', '1.3.0']
    _UPDATE_MODULES = [update_1_1_0_to_1_3_0.step_updater]
    src_idx = _UPDATE_NODES.index(eq_src_ver)
    dst_idx = _UPDATE_NODES.index(eq_dst_ver)
    return [getattr(m, 'update_all') for m in _UPDATE_MODULES[src_idx:dst_idx]]
