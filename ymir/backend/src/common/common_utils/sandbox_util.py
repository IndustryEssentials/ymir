from collections import defaultdict
import os
import re
from typing import List, Dict, Set

import yaml

from id_definition.error_codes import UpdaterErrorCode
from id_definition.task_id import IDProto
from mir import version
from mir.scm.cmd import CmdScm


class SandboxError(Exception):
    def __init__(self, error_code: int, error_message: str) -> None:
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self) -> str:
        return f"code: {self.error_code}, message: {self.error_message}"


def detect_sandbox_src_ver(sandbox_root: str) -> str:
    """
    detect user space versions in this sandbox

    Args:
        sandbox_root (str): root of this sandbox

    Returns:
        str: sandbox version

    Raises:
        SandboxError if labels.yaml not found, or can not be parsed as yaml;
        found no user space version or multiple user space versions.
    """
    user_to_repos = detect_users_and_repos(sandbox_root)
    ver_to_users: Dict[str, List[str]] = defaultdict(list)
    for user_id in user_to_repos:
        user_label_file = os.path.join(sandbox_root, user_id, 'labels.yaml')
        try:
            with open(user_label_file, 'r') as f:
                user_label_dict = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise SandboxError(error_code=UpdaterErrorCode.INVALID_USER_LABEL_FILE,
                               error_message=f"invalid label file: {user_label_file}") from e

        ver_to_users[user_label_dict.get('ymir_version', version.DEFAULT_YMIR_SRC_VERSION)].append(user_id)

    if len(ver_to_users) != 1:
        raise SandboxError(error_code=UpdaterErrorCode.INVALID_USER_SPACE_VERSIONS,
                           error_message=f"invalid user space versions: {ver_to_users}")

    return list(ver_to_users.keys())[0]


def detect_users_and_repos(sandbox_root: str) -> Dict[str, Set[str]]:
    """
    detect user and repo directories in this sandbox

    Args:
        sandbox_root (str): root of this sandbox

    Returns:
        Dict[str, Set[str]]: key: user id, value: repo ids
    """
    user_to_repos = defaultdict(set)
    for user_id in os.listdir(sandbox_root):
        match_result = re.match(f"\\d{{{IDProto.ID_LEN_USER_ID}}}", user_id)
        if not match_result:
            continue
        user_dir = os.path.join(sandbox_root, user_id)
        user_to_repos[user_id].update([
            repo_id for repo_id in os.listdir(user_dir) if re.match(f"\\d{{{IDProto.ID_LEN_REPO_ID}}}", repo_id)
            and os.path.isdir(os.path.join(user_dir, repo_id, '.git'))
        ])
    return user_to_repos
