import logging
import os
import shutil
from typing import Callable, List

from common_utils.sandbox_util import detect_users_and_repos, SandboxError
from common_utils.version import ymir_salient_version
from id_definition.error_codes import UpdaterErrorCode

from update_1_1_0_to_1_3_0.step_updater import update_all as update_110_130


def update(sandbox_root: str, src_ver: str, dst_ver: str) -> None:
    steps: List[Callable[[str], None]] = _get_update_steps(src_ver=src_ver, dst_ver=dst_ver)
    if not steps:
        logging.info('nothing to update {src_ver}:{dst_ver}')
        return

    _backup(sandbox_root)

    # update
    user_to_repos = detect_users_and_repos(sandbox_root)
    try:
        for update_func in steps:
            for user_id, repo_ids in user_to_repos.items():
                for repo_id in repo_ids:
                    update_func(os.path.join(sandbox_root, user_id, repo_id))
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


def _get_update_steps(src_ver: str, dst_ver: str) -> List[Callable[[str], None]]:
    eq_src_ver = ymir_salient_version(src_ver)
    eq_dst_ver = ymir_salient_version(dst_ver)

    _UPDATE_NODES: List[str] = ['1.1.0', '1.3.0']
    _UPDATE_FUNCS: List[Callable[[str], None]] = [update_110_130]
    return _UPDATE_FUNCS[_UPDATE_NODES.index(eq_src_ver):_UPDATE_NODES.index(eq_dst_ver)]
