
from typing import List

from mir.scm.cmd import CmdScm


def get_repo_tags(mir_root: str) -> List[str]:
    git_cmd = CmdScm(working_dir=mir_root, scm_executable='git')
    tags: str = git_cmd.tag()
    return sorted(tags.splitlines())
