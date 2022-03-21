"""
use this module to read contents in other branch head ref or from other tags \n
some mir commands, such as `mir search`, `mir merge` will use this module
"""

import logging
import os
from typing import Any

from mir import scm
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from pydantic import FilePath


def locate_file_in_rev(mir_root: str, file_name: str, rev: str) -> str:
    """
    get the file location in mir_root for special rev
    Args:
    mir_root: root to a mir repo
    file_name: name of the mir file
    rev: branch name, commit id, or tag name
    """
    if not mir_root or not file_name or not rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid args')

    scm_git = scm.Scm(mir_root if mir_root else ".", scm_executable="git")

    # get `file_name` sha1
    blob_hash = scm_git.rev_parse(f"{rev}:{file_name}")
    if not blob_hash:
        raise MirRuntimeError(MirCode.RC_CMD_INVALID_MIR_REPO, f"found no file: {file_name}")
    out_str = scm_git.tree([blob_hash])
    logging.info(f"out str: {out_str}")

    file_path = os.path.join(mir_root, ".git/objects", blob_hash[:2], blob_hash[2:])
    return file_path


class open_mir():
    __slots__ = ("_file_name", "_rev", "_mode", "_fd", "_mir_root")

    def __init__(self, mir_root: str, file_name: str, rev: str, mode: str):
        self._mir_root = mir_root
        self._file_name = file_name
        self._rev = rev
        self._mode = mode
        self._fd = None

    def __enter__(self) -> Any:
        if not self._mir_root or not self._file_name or not self._rev or not self._mode:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid arguments')

        file_path = locate_file_in_rev(mir_root=self._mir_root, file_name=self._file_name, rev=self._rev)
        self._fd = open(file_path, self._mode)
        return self._fd

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        if self._fd is not None:
            self._fd.close()
            self._fd = None
