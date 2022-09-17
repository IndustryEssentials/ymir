from collections import defaultdict
import os
import re
from typing import List, Dict, Set

import yaml

from id_definition.error_codes import UpdateErrorCode
from id_definition.task_id import IDProto
from mir import version

_USER_ID_PATTERN = f"\\d{{{IDProto.ID_LEN_USER_ID}}}"  # r'\d{4}'
_REPO_ID_PATTERN = f"\\d{{{IDProto.ID_LEN_REPO_ID}}}"  # r'\d{6}'


class SandboxError(Exception):
    def __init__(self, error_code: int, error_message: str) -> None:
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self) -> str:
        return f"code: {self.error_code}, content: {self.error_message}"


def detect_users_and_repos(sandbox_root: str) -> Dict[str, Set[str]]:
    """
    detect user and repo directories in this sandbox

    Args:
        sandbox_root (str): root of this sandbox
    Returns:
        Dict[str, List[str]]: key: user id, value: repo ids
    """
    user_to_repos = defaultdict(set)
    for user_id in os.listdir(sandbox_root):
        match_result = re.match(_USER_ID_PATTERN, user_id)
        if not match_result:
            continue
        user_dir = os.path.join(sandbox_root, user_id)
        user_to_repos[user_id].update([
            repo_id for repo_id in os.listdir(user_dir)
            if re.match(_REPO_ID_PATTERN, repo_id) and os.path.isdir(os.path.join(user_dir, repo_id, '.git'))
        ])
    return user_to_repos


def detect_sandbox_src_ver(sandbox_root: str) -> str:
    """
    detect user space versions in this sandbox
    """
    user_to_repos = detect_users_and_repos(sandbox_root)
    ver_to_users: Dict[str, List[str]] = defaultdict(list)
    for user_id in user_to_repos:
        user_label_file = os.path.join(sandbox_root, user_id, 'labels.yaml')
        try:
            with open(user_label_file, 'r') as f:
                user_label_dict = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise SandboxError(error_code=UpdateErrorCode.INVALID_USER_LABEL_FILE,
                               error_message=f"invalid label file: {user_label_file}") from e

        ver_to_users[user_label_dict.get('ymir_version', version.DEFAULT_YMIR_SRC_VERSION)].append(user_id)

    if len(ver_to_users) != 1:
        raise SandboxError(error_code=UpdateErrorCode.INVALID_USER_SPACE_VERSIONS,
                           error_message=f"invalid user space versions: {ver_to_users}")

    return list(ver_to_users.keys())[0]
