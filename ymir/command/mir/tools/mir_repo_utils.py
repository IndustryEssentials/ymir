import logging
import os
from typing import List, Optional

from mir import scm

from mir.tools import mir_storage


def find_extra_items(mir_root: str) -> List[str]:
    """
    find all extra items not in mir_settings.MIR_FILES_LIST
    """
    items = os.listdir(path=mir_root)
    return list(set(items) - set(mir_storage.get_all_mir_paths()) - set(mir_storage.MIR_ASSOCIATED_FILES))


def mir_check_repo_git_dirty(mir_root: str = ".") -> bool:
    git_scm = scm.Scm(mir_root, scm_executable="git")
    git_result = git_scm.status("-s")  # if clean, returns nothing
    if (git_result or len(git_result) > 0):
        logging.info(f"git result: \n{git_result}")
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
