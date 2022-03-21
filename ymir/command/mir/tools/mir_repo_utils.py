import logging
import os
from typing import Optional

from mir import scm


def mir_check_repo_git_dirty(mir_root: str = ".") -> bool:
    git_scm = scm.Scm(mir_root, scm_executable="git")
    git_result = git_scm.status("-s")  # if clean, returns nothing
    if (git_result or len(git_result) > 0):
        logging.info(f"{git_result}")
        return True
    return False  # clean


def mir_check_branch_exists(mir_root: str, branch: str) -> bool:
    try:
        git_scm = scm.Scm(mir_root, scm_executable="git")
        git_scm.rev_parse(branch)
        return True
    except Exception:
        # git rev-parse will return non-zero code when can not find branch
        # and cmd.py packs non-zero return code as an error
        return False


def work_dir_to_monitor_file(work_dir: Optional[str]) -> Optional[str]:
    return os.path.join(work_dir, 'out', 'monitor.txt') if work_dir else None
