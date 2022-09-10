from collections import defaultdict
from enum import IntEnum
import logging
import os
import re
from typing import List, Dict, Set

import yaml

from error_codes import UpgradeErrorCode


_USER_ID_PATTERN = '\d{4}'
_REPO_ID_PATTERN = '\d{6}'
_DEFAULT_YMIR_SRC_VERSION = '1.1.0'


class SandboxState(IntEnum):
    VALID = 0

    SANDBOX_STATE_UNKNOWN = UpgradeErrorCode.SANDBOX_STATE_UNKNOWN
    MULTIPLE_USER_SPACE_VERSIONS = UpgradeErrorCode.MULTIPLE_USER_SPACE_VERSIONS
    INVALID_USER_LABEL_FILE = UpgradeErrorCode.INVALID_USER_LABEL_FILE


class SandboxInfo:
    def __init__(self, root: str = '') -> None:
        self.root = root
        self.src_ver = ''
        self.user_to_repos: Dict[str, Set[str]] = defaultdict(set)
        self.state = SandboxState.SANDBOX_STATE_UNKNOWN

        self._detect_users_and_repos()
        self._detect_sandbox_src_ver()

    def _detect_users_and_repos(self) -> None:
        """
        detect user and repo directories in this sandbox

        Side Effects:
            `self.user_to_repos` will be filled
        """
        for user_id in os.listdir(self.root):
            match_result = re.match(pattern=_USER_ID_PATTERN, string=user_id)
            if not match_result:
                continue
            user_dir = os.path.join(self.root, user_id)
            if not os.path.isdir(user_dir):
                continue

            for repo_id in os.listdir(user_dir):
                if not re.match(pattern=_REPO_ID_PATTERN, string=repo_id):
                    continue
                repo_dir = os.path.join(user_dir, repo_id)
                if not os.path.isdir(repo_dir):
                    continue

                self.user_to_repos[user_id].add(repo_id)

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
            except (FileNotFoundError, yaml.YAMLError):
                logging.error(f"invalid label file: {user_label_file}")
                self.state = SandboxState.INVALID_USER_LABEL_FILE
            ver_to_users[user_label_dict.get('ymir_version', _DEFAULT_YMIR_SRC_VERSION)].append(user_id)

        if len(ver_to_users) > 1:
            logging.error(f"multiple user space versions: {ver_to_users}")
            self.state = SandboxState.MULTIPLE_USER_SPACE_VERSIONS

        self.src_ver = list(ver_to_users.keys())[0] if ver_to_users else _DEFAULT_YMIR_SRC_VERSION
        self.state = SandboxState.VALID
