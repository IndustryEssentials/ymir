import os
from typing import Iterable, List, Tuple

from common_utils import sandbox
from mir.scm.cmd import CmdScm


def walk(sandbox_root: str) -> Iterable[Tuple[str, str]]:
    user_to_repos = sandbox.detect_users_and_repos(sandbox_root)
    for user_id, repo_ids in user_to_repos.items():
        for repo_id in repo_ids:
            mir_root = os.path.join(sandbox_root, user_id, repo_id)

            repo_git = CmdScm(working_dir=mir_root, scm_executable='git')
            tags: List[str] = repo_git.tag().splitlines()
            for tag in tags:
                if tag == 'master':
                    continue
                yield (mir_root, tag)
