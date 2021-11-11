import json
import logging
import os
from typing import Optional

from mir import scm
from mir.tools import mir_storage


def mir_check_repo_dvc_dirty(mir_root: str = ".") -> bool:
    names = [name for name in mir_storage.get_all_mir_paths() if os.path.isfile(os.path.join(mir_root, name))]
    if names:
        dvc_cmd_args = ["--show-json", "--targets"]
        dvc_cmd_args.extend(names)
        dvc_scm = scm.Scm(mir_root, scm_executable="dvc")
        dvc_result = dvc_scm.diff(dvc_cmd_args)
        json_object = json.loads(dvc_result)

        keys = ['added', 'deleted', 'modified', 'renamed', 'not in cache']
        dvc_dirty = False
        for key in keys:
            dirty_value = json_object.get(key, None)
            if dirty_value:
                logging.info(f"{key}: {dirty_value}")
                dvc_dirty = True

        return dvc_dirty
    else:
        # if no mir files in this mir repo, it's clean
        return False


def mir_check_repo_git_dirty(mir_root: str = ".") -> bool:
    git_scm = scm.Scm(mir_root, scm_executable="git")
    git_result = git_scm.status("-s")  # if clean, returns nothing
    if (git_result or len(git_result) > 0):
        logging.info(f"{git_result}")
        return True
    return False  # clean


def mir_check_repo_dirty(mir_root: str = '.') -> bool:
    return mir_check_repo_dvc_dirty(mir_root) or mir_check_repo_git_dirty(mir_root)


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
