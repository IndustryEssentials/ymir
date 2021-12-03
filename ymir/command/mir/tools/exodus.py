"""
use this module to read contents in other branch head ref or from other tags \n
some mir commands, such as `mir search`, `mir merge` will use this module
"""

import os
from typing import Any, Optional

import yaml

from mir import scm
from mir.tools.code import MirCode


class ExodusError(Exception):
    __slots__ = ("code")

    def __init__(self, msg: str, code: int) -> None:
        super().__init__(msg)
        self.code = code


def locate_file_in_rev(mir_root: str, file_name: str, rev: str) -> str:
    """
    get the file location in mir_root for special rev
    Args:
    mir_root: root to a mir repo
    file_name: name of the mir file
    rev: branch name, commit id, or tag name
    """
    if not mir_root or not file_name or not rev:
        raise ValueError("invalid args")

    scm_git = scm.Scm(mir_root if mir_root else ".", scm_executable="git")

    # get `file_name`.dvc sha1
    # using git command: git rev-parse <rev>:<file_name>
    dvc_sha1 = scm_git.rev_parse("{}:{}.dvc".format(rev, file_name))
    if not dvc_sha1:
        raise ExodusError("found no dvc file: {}".format(file_name), code=MirCode.RC_CMD_INVALID_MIR_FILE)

    # parse `file_name`.dvc to get file_name's sha1
    # using git command: git cat-file -p `dvc_sha1`
    # result should like:
    #   outs:
    #   - md5: ffa21df3e9741af03f60a60bb171e4a1
    #     size: 7304832
    #     path: keywords.mir
    # which is dvc format, get md5 and store it to `file_hash`
    dvc_file_str = scm_git.cat_file(["-p", dvc_sha1])
    dvc_file_yaml_data = yaml.safe_load(dvc_file_str)
    if not dvc_file_yaml_data.get("outs", None):
        raise ExodusError("found no singnature for file: {}".format(file_name),
                          code=MirCode.RC_CMD_INVALID_MIR_FILE)

    file_hash = None  # type: Optional[str]
    out_list = dvc_file_yaml_data["outs"]
    for val in out_list:
        if val["path"] == file_name:
            file_hash = val["md5"]
            break

    if not file_hash:
        raise ExodusError("found no singnature for file: {}".format(file_name),
                          code=MirCode.RC_CMD_INVALID_MIR_FILE)

    # open that file (it's in .dvc/cache) and return `file_name`
    file_path = os.path.join(mir_root, ".dvc/cache", file_hash[:2], file_hash[2:])
    return file_path


def _open_branch_tag_commit_file(mir_root: str, file_name: str, rev: str, mode: str) -> Any:
    """
    Opens file in mir repo from specific branch, tag or commit id
    Args:
        mir_root: root dir of mir repo
        file_name: mir file name
        rev: branch name, tag name or commit id
        mode: file open mode, same as in `open` function
    Returns:
        file descriptor or something
    Raises:
        io errors
    """
    if not rev:  # explict set rev, if use current rev, set to HEAD
        raise ExodusError("found no rev", code=MirCode.RC_CMD_INVALID_ARGS)
    file_path = locate_file_in_rev(mir_root, file_name, rev)
    return open(file_path, mode)


class open_mir():
    __slots__ = ("_file_name", "_rev", "_mode", "_fd", "_mir_root")

    def __init__(self, mir_root: str, file_name: str, rev: str, mode: str):
        self._mir_root = mir_root
        self._file_name = file_name
        self._rev = rev
        self._mode = mode
        self._fd = None

    def __enter__(self) -> Any:
        if not self._mir_root or not self._file_name or not self._mode:
            raise ValueError("invalid arguments")

        self._fd = _open_branch_tag_commit_file(mir_root=self._mir_root,
                                                file_name=self._file_name,
                                                rev=self._rev,
                                                mode=self._mode)
        return self._fd

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        if self._fd is not None:
            self._fd.close()
            self._fd = None
