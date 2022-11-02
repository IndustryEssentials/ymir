import enum
import logging
import os
import sys
from typing import Callable, List

from mir.tools import mir_repo_utils
from mir.tools.code import MirCode


@enum.unique
class Prerequisites(enum.IntEnum):
    NOTHING = 0
    IS_INSIDE_GIT_REPO = enum.auto()
    IS_OUTSIDE_GIT_REPO = enum.auto()
    IS_INSIDE_MIR_REPO = enum.auto()
    IS_OUTSIDE_MIR_REPO = enum.auto()
    IS_DIRTY = enum.auto()
    IS_CLEAN = enum.auto()


_DEFAULT_PREREQUISTITES = [Prerequisites.IS_INSIDE_MIR_REPO, Prerequisites.IS_CLEAN]


# error messages for check failed (if prerequisites not satisfied)
_ERROR_INFOS = {
    Prerequisites.NOTHING: '',
    Prerequisites.IS_INSIDE_GIT_REPO: 'mir_root is not a git repo',
    Prerequisites.IS_OUTSIDE_GIT_REPO: 'mir_root is already a git repo',
    Prerequisites.IS_INSIDE_MIR_REPO: 'mir_root is not a mir repo',
    Prerequisites.IS_OUTSIDE_MIR_REPO: 'mir_root is already a mir repo',
    Prerequisites.IS_DIRTY: 'mir repo is clean (need dirty)',
    Prerequisites.IS_CLEAN: 'mir repo is dirty (need clean)',
}


# check mir root
def check(mir_root: str, prerequisites: List[Prerequisites] = _DEFAULT_PREREQUISTITES) -> int:
    if not mir_root.startswith('/'):
        logging.warning(f"check failed: invalid mir_root: {mir_root or '(empty)'}, needs absolute path")
        return MirCode.RC_CMD_INVALID_ARGS

    for item in prerequisites:
        checker_func: Callable = getattr(sys.modules[__name__], f"_check_{item.name.lower()}")
        return_code = checker_func(mir_root)
        if return_code != MirCode.RC_OK:
            logging.error(f"check failed: {_ERROR_INFOS[item]}")
            return return_code
    return MirCode.RC_OK


def _check_nothing(mir_root: str) -> int:
    return MirCode.RC_OK


def _check_is_inside_git_repo(mir_root: str) -> int:
    return (MirCode.RC_OK if os.path.isdir(os.path.join(mir_root, ".git")) else MirCode.RC_CMD_INVALID_ARGS)


def _check_is_outside_git_repo(mir_root: str) -> int:
    return (MirCode.RC_OK if not os.path.isdir(os.path.join(mir_root, ".git")) else MirCode.RC_CMD_INVALID_ARGS)


def _check_is_inside_mir_repo(mir_root: str) -> int:
    return (MirCode.RC_OK if os.path.isdir(os.path.join(mir_root, ".git"))
            and os.path.isdir(os.path.join(mir_root, ".mir")) else MirCode.RC_CMD_INVALID_MIR_REPO)


def _check_is_outside_mir_repo(mir_root: str) -> int:
    return (MirCode.RC_OK if not os.path.isdir(os.path.join(mir_root, ".git"))
            or not os.path.isdir(os.path.join(mir_root, ".mir")) else MirCode.RC_CMD_INVALID_ARGS)


def _check_is_dirty(mir_root: str) -> int:
    is_dirty = mir_repo_utils.mir_check_repo_git_dirty(mir_root)
    return MirCode.RC_OK if is_dirty else MirCode.RC_CMD_INVALID_ARGS


def _check_is_clean(mir_root: str) -> int:
    is_dirty = mir_repo_utils.mir_check_repo_git_dirty(mir_root)
    return MirCode.RC_OK if not is_dirty else MirCode.RC_CMD_DIRTY_REPO
