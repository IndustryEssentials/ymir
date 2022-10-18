from collections import defaultdict
import logging
import os
import re
from typing import List, Dict, Set

import yaml

from common_utils.version import DEFAULT_YMIR_SRC_VERSION
from id_definition.error_codes import UpdaterErrorCode
from id_definition.task_id import IDProto


class SandboxError(Exception):
    def __init__(self, error_code: int, error_message: str) -> None:
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self) -> str:
        return f"code: {self.error_code}, message: {self.error_message}"


def detect_sandbox_src_versions(sandbox_root: str) -> List[str]:
    """
    detect user space versions in this sandbox

    Args:
        sandbox_root (str): root of this sandbox

    Returns:
        str: sandbox versions

    Raises:
        SandboxError if labels.yaml not found, or can not be parsed as yaml;
        found no user space version or multiple user space versions.
    """
    user_to_repos = detect_users_and_repos(sandbox_root)
    if not user_to_repos:
        logging.warning(f"can not find user and repos in sandbox: {sandbox_root}")
        return []

    ver_to_users: Dict[str, List[str]] = defaultdict(list)
    for user_id in user_to_repos:
        user_label_file = os.path.join(sandbox_root, user_id, 'labels.yaml')
        try:
            with open(user_label_file, 'r') as f:
                user_label_dict = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise SandboxError(error_code=UpdaterErrorCode.INVALID_USER_LABEL_FILE,
                               error_message=f"invalid label file: {user_label_file}") from e

        ver_to_users[user_label_dict.get('ymir_version', DEFAULT_YMIR_SRC_VERSION)].append(user_id)

    if len(ver_to_users) > 1:
        logging.info(f"[detect_sandbox_src_versions]: multiple sandbox versions detected: {ver_to_users}")

    return list(ver_to_users.keys())


def detect_users_and_repos(sandbox_root: str) -> Dict[str, Set[str]]:
    """
    detect user and repo directories in this sandbox

    Args:
        sandbox_root (str): root of this sandbox

    Returns:
        Dict[str, Set[str]]: key: user id, value: repo ids
    """
    if not os.path.isdir(sandbox_root):
        logging.warning(f"sandbox not exists: {sandbox_root}")
        return {}

    user_to_repos = defaultdict(set)
    for user_id in os.listdir(sandbox_root):
        match_result = re.match(f"^\\d{{{IDProto.ID_LEN_USER_ID}}}$", user_id)
        if not match_result:
            continue
        user_dir = os.path.join(sandbox_root, user_id)
        user_to_repos[user_id].update([
            repo_id for repo_id in os.listdir(user_dir) if re.match(f"^\\d{{{IDProto.ID_LEN_REPO_ID}}}$", repo_id)
            and os.path.isdir(os.path.join(user_dir, repo_id, '.git'))
        ])
    return user_to_repos


def check_sandbox(sandbox_root: str) -> None:
    user_to_repos = detect_users_and_repos(sandbox_root)
    for user_id, repo_ids in user_to_repos.items():
        user_labels_path = os.path.join(sandbox_root, user_id, 'labels.yaml')
        if not os.path.isfile(user_labels_path):
            raise SandboxError(error_code=UpdaterErrorCode.INVALID_USER_LABEL_FILE,
                               error_message=f"Invalid user labels: {user_labels_path} is not a file")

        user_labels_inode = os.stat(user_labels_path).st_ino
        for repo_id in repo_ids:
            repo_labels_path = os.path.join(sandbox_root, user_id, repo_id, '.mir', 'labels.yaml')
            if os.path.islink(repo_labels_path):
                if os.path.realpath(repo_labels_path) != user_labels_path:
                    raise SandboxError(
                        error_code=UpdaterErrorCode.INVALID_USER_LABEL_FILE,
                        error_message=f"Invalid user labels: {user_labels_path} not symlinked to user labels")
            else:
                if os.stat(repo_labels_path).st_ino != user_labels_inode:
                    raise SandboxError(
                        error_code=UpdaterErrorCode.INVALID_USER_LABEL_FILE,
                        error_message=f"Invalid user labels: {user_labels_path} not hardlinked to user labels")
