import enum
import logging
import os
import sys
from typing import Callable, List, Union

from mir.tools import class_ids, mir_repo_utils
from mir.tools.code import MirCode
from mir.tools.revs_parser import TypRevTid


@enum.unique
class Prerequisites(enum.IntEnum):
    NOTHING = 0
    IS_INSIDE_GIT_REPO = enum.auto()
    IS_OUTSIDE_GIT_REPO = enum.auto()
    IS_INSIDE_MIR_REPO = enum.auto()
    IS_OUTSIDE_MIR_REPO = enum.auto()
    IS_DIRTY = enum.auto()
    IS_CLEAN = enum.auto()
    HAVE_LABELS = enum.auto()
    HAVE_NO_LABELS = enum.auto()


_DEFAULT_PREREQUISTITES = [Prerequisites.IS_INSIDE_MIR_REPO, Prerequisites.IS_CLEAN, Prerequisites.HAVE_LABELS]


# error messages for check failed (if prerequisites not satisfied)
_ERROR_INFOS = {
    Prerequisites.NOTHING: '',
    Prerequisites.IS_INSIDE_GIT_REPO: 'mir_root is not a git repo',
    Prerequisites.IS_OUTSIDE_GIT_REPO: 'mir_root is already a git repo',
    Prerequisites.IS_INSIDE_MIR_REPO: 'mir_root is not a mir repo',
    Prerequisites.IS_OUTSIDE_MIR_REPO: 'mir_root is already a mir repo',
    Prerequisites.IS_DIRTY: 'mir repo is clean, nothing to commit',
    Prerequisites.IS_CLEAN: 'mir repo is dirty',
    Prerequisites.HAVE_LABELS: f"can not find {class_ids.ids_file_name()}",
    Prerequisites.HAVE_NO_LABELS: f"already have {class_ids.ids_file_name()}",
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
            and os.path.isdir(os.path.join(mir_root, ".dvc")) else MirCode.RC_CMD_INVALID_MIR_REPO)


def _check_is_outside_mir_repo(mir_root: str) -> int:
    return (MirCode.RC_OK if not os.path.isdir(os.path.join(mir_root, ".git"))
            or not os.path.isdir(os.path.join(mir_root, ".dvc")) else MirCode.RC_CMD_INVALID_ARGS)


def _check_is_dirty(mir_root: str) -> int:
    is_dirty = mir_repo_utils.mir_check_repo_dirty(mir_root)
    return MirCode.RC_OK if is_dirty else MirCode.RC_CMD_INVALID_ARGS


def _check_is_clean(mir_root: str) -> int:
    is_dirty = mir_repo_utils.mir_check_repo_dirty(mir_root)
    return MirCode.RC_OK if not is_dirty else MirCode.RC_CMD_DIRTY_REPO


def _check_have_labels(mir_root: str) -> int:
    have_labels = os.path.isfile(class_ids.ids_file_path(mir_root))
    return MirCode.RC_OK if have_labels else MirCode.RC_CMD_INVALID_MIR_REPO


def _check_have_no_labels(mir_root: str) -> int:
    have_labels = os.path.isfile(class_ids.ids_file_path(mir_root))
    return MirCode.RC_OK if not have_labels else MirCode.RC_CMD_INVALID_MIR_REPO


def check_src_revs(revs: Union[List[TypRevTid], TypRevTid]) -> int:
    if isinstance(revs, list):
        if len(revs) == 0:
            logging.error('invalid args: empty --src-revs')
            return MirCode.RC_CMD_INVALID_ARGS
        for rev in revs:
            result = check_src_revs(rev)
            if result != MirCode.RC_OK:
                return result
    elif isinstance(revs, TypRevTid):
        if not revs.rev:
            logging.error(f"invalid args: no rev in --src-revs: {revs}")
            return MirCode.RC_CMD_INVALID_ARGS
    else:
        return MirCode.RC_CMD_INVALID_ARGS

    return MirCode.RC_OK


def check_dst_rev(dst_typ_rev_tid: TypRevTid) -> int:
    if not dst_typ_rev_tid.rev:
        logging.error(f"invalid args: no rev in --dst-rev: {dst_typ_rev_tid}")
        return MirCode.RC_CMD_INVALID_ARGS
    if not dst_typ_rev_tid.tid:
        logging.error(f"invalid args: no tid in --dst-rev: {dst_typ_rev_tid}")
        return MirCode.RC_CMD_INVALID_ARGS
    return MirCode.RC_OK
