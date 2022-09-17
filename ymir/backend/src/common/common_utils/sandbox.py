from collections import defaultdict
import os
import re
from typing import List, Dict, Set

import yaml

from id_definition.error_codes import UpdateErrorCode
from id_definition.task_id import IDProto

_USER_ID_PATTERN = f"\\d{{{IDProto.ID_LEN_USER_ID}}}"  # r'\d{4}'
_REPO_ID_PATTERN = f"\\d{{{IDProto.ID_LEN_REPO_ID}}}"  # r'\d{6}'
_DEFAULT_YMIR_SRC_VERSION = '1.1.0'


class SandboxError(Exception):
    def __init__(self, error_code: int, error_message: str) -> None:
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self) -> str:
        return f"code: {self.error_code}, content: {self.error_message}"


class SandboxInfo:
    def __init__(self, root: str = '') -> None:
        self.root = root
        self.src_ver = ''
        self.user_to_repos: Dict[str, Set[str]] = defaultdict(set)

        self._detect_users_and_repos()
        self._detect_sandbox_src_ver()

    def _detect_users_and_repos(self) -> None:
        """
        detect user and repo directories in this sandbox

        Side Effects:
            `self.user_to_repos` will be filled with all users and repos in this sandbox
        """
        for user_id in os.listdir(self.root):
            match_result = re.match(_USER_ID_PATTERN, user_id)
            if not match_result:
                continue
            user_dir = os.path.join(self.root, user_id)
            if not os.path.isdir(user_dir):
                continue

            self.user_to_repos[user_id].update([
                repo_id for repo_id in os.listdir(user_dir)
                if re.match(_REPO_ID_PATTERN, repo_id) and os.path.isdir(os.path.join(user_dir, repo_id))
            ])

    def _detect_sandbox_src_ver(self) -> None:
        """
        detect user space versions in this sandbox

        Side Effects:
            `self.state` and `self.src_ver` will be reset
        """
        ver_to_users: Dict[str, List[str]] = defaultdict(list)
        for user_id in self.user_to_repos:
            user_label_file = os.path.join(self.root, user_id, 'labels.yaml')
            try:
                with open(user_label_file, 'r') as f:
                    user_label_dict = yaml.safe_load(f)
            except (FileNotFoundError, yaml.YAMLError) as e:
                raise SandboxError(error_code=UpdateErrorCode.INVALID_USER_LABEL_FILE,
                                   error_message=f"invalid label file: {user_label_file}") from e

            ver_to_users[user_label_dict.get('ymir_version', _DEFAULT_YMIR_SRC_VERSION)].append(user_id)

        if len(ver_to_users) > 1:
            raise SandboxError(error_code=UpdateErrorCode.MULTIPLE_USER_SPACE_VERSIONS,
                               error_message=f"multiple user space versions: {ver_to_users}")

        self.src_ver = list(ver_to_users.keys())[0] if ver_to_users else _DEFAULT_YMIR_SRC_VERSION
