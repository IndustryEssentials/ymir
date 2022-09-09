from collections import defaultdict
import logging
import os
import re
import shutil
import sys
from typing import Callable, Dict, List, Set, Tuple

import yaml

import errors as update_errors
import settings as update_settings
from version import YMIR_VERSION

import update_1_1_0_to_1_3_0.step_updater


_DEFAULT_YMIR_SRC_VERSION = '1.1.0'

_UPDATE_STEPS: Dict[Tuple[str, str], Tuple[str, ...]] = {
    ('1.1.0', '1.3.0'): ('update_1_1_0_to_1_3_0.step_updater',),
}


class _SandboxInfo:
    def __init__(self, root: str = '') -> None:
        self.root = root
        self.src_ver = ''
        self.user_to_repos: Dict[str, Set[str]] = defaultdict(set)


def _detect_user_and_repos(sandbox_info: _SandboxInfo) -> None:
    for user_id in os.listdir(sandbox_info.root):
        match_result = re.match(pattern=update_settings.USER_ID_PATTERN, string=user_id)
        if not match_result:
            continue
        user_dir = os.path.join(sandbox_info.root, user_id)
        if not os.path.isdir(user_dir):
            continue

        for repo_id in os.listdir(user_dir):
            if not re.match(pattern=update_settings.REPO_ID_PATTERN, string=repo_id):
                continue
            repo_dir = os.path.join(user_dir, repo_id)
            if not os.path.isdir(repo_dir):
                continue

            sandbox_info.user_to_repos[user_id].add(repo_id)


def _detect_sandbox_src_ver(sandbox_info: _SandboxInfo) -> None:
    ver_to_users: Dict[str, List[str]] = defaultdict(list)
    for user_id in sandbox_info.user_to_repos:
        user_label_file = os.path.join(sandbox_info.root, user_id, 'labels.yaml')
        try:
            with open(user_label_file, 'r') as f:
                user_label_dict = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise update_errors.InvalidUserLabelFile(user_label_file=user_label_file)
        ver_to_users[user_label_dict.get('ymir_version', _DEFAULT_YMIR_SRC_VERSION)].append(user_id)

    if len(ver_to_users) > 1:
        raise update_errors.MultipleUserSpaceVersions(ver_to_users=ver_to_users)

    sandbox_info.src_ver = list(ver_to_users.keys())[0]


def _exc_update_steps(update_steps: Tuple[str, ...], sandbox_info: _SandboxInfo) -> None:
    for step_module_name in update_steps:
        logging.info(f"step: {step_module_name}")
        step_module = sys.modules[step_module_name]
        step_func: Callable = getattr(step_module, 'update_sandbox')
        step_func()


def _backup(sandbox_info: _SandboxInfo) -> str:
    backup_dir = os.path.join(sandbox_info.root, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    if os.listdir(backup_dir):
        raise update_errors.BackupDirNotEmpty(backup_dir)

    for user_id, repo_ids in sandbox_info.user_to_repos.items():
        src_user_dir = os.path.join(sandbox_info.root, user_id)
        dst_user_dir = os.path.join(backup_dir, user_id)
        _copy_user_space(src_user_dir=src_user_dir, dst_user_dir=dst_user_dir, repo_ids=repo_ids)

    return backup_dir


def _roll_back(backup_dir: str, sandbox_info: _SandboxInfo) -> None:
    for user_id, repo_ids in sandbox_info.user_to_repos.items():
        src_user_dir = os.path.join(backup_dir, user_id)
        dst_user_dir = os.path.join(sandbox_info.root, user_id)
        shutil.rmtree(dst_user_dir)
        _copy_user_space(src_user_dir=src_user_dir, dst_user_dir=dst_user_dir, repo_ids=repo_ids)


def _copy_user_space(src_user_dir: str, dst_user_dir: str, repo_ids: Set[str]) -> None:
    shutil.copy(src=os.path.join(src_user_dir, 'labels.yaml'),
                dst=os.path.join(dst_user_dir, 'labels.yaml'))
    for repo_id in repo_ids:
        shutil.copytree(src=os.path.join())


def main() -> int:
    sandbox_info = _SandboxInfo(root=os.environ['BACKEND_SANDBOX_ROOT'])
    _detect_user_and_repos(sandbox_info)
    if not sandbox_info.user_to_repos:
        logging.info('no need to update: found no users')
        return 0

    _detect_sandbox_src_ver(sandbox_info)
    update_steps = _UPDATE_STEPS.get((sandbox_info.src_ver, YMIR_VERSION), [])
    if not update_steps:
        logging.info('no need to update')
        return 0

    backup_dir = _backup(sandbox_info)
    try:
        _exc_update_steps(update_steps=update_steps, sandbox_info=sandbox_info)
    except Exception as e:
        _roll_back(backup_dir=backup_dir, sandbox_info=sandbox_info)
        raise e

    shutil.rmtree(backup_dir)

    return 0


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s]: %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)
    sys.exit(main())
