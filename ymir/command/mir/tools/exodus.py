"""
use this module to read contents in other branch head ref or from other tags \n
some mir commands, such as `mir search`, `mir merge` will use this module
"""

import io
import os
import subprocess

from mir import scm
from mir.scm.cmd import stream_copy
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def read_mir(mir_root: str, rev: str, file_name: str) -> bytes:
    if not mir_root or not file_name or not rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid args')

    scm_git = scm.Scm(mir_root if mir_root else ".", scm_executable="git")
    blob_hash = scm_git.rev_parse(f"{rev}:{file_name}")
    if not blob_hash:
        raise MirRuntimeError(MirCode.RC_CMD_INVALID_MIR_REPO, f"found no file: {rev}:{file_name}")

    if os.path.isfile(os.path.join(mir_root, '.gitattributes')):
        # git lfs: git cat-file -p blob_hash | git lfs smudge
        catfile_ps = subprocess.Popen(['git', 'cat-file', '-p', blob_hash], stdout=subprocess.PIPE, cwd=mir_root)
        smudge_ps = subprocess.Popen(['git', 'lfs', 'smudge'],
                                     stdin=catfile_ps.stdout,
                                     stdout=subprocess.PIPE,
                                     cwd=mir_root)

        bio = io.BytesIO()
        stream_copy(source=smudge_ps.stdout, destination=bio, chunk_size=io.DEFAULT_BUFFER_SIZE)
        return bio.getvalue()
    else:
        # git without lfs: git cat-file -p blob_hash
        bio = io.BytesIO()
        scm_git.cat_file(['-p', blob_hash], output_stream=bio)
        return bio.getvalue()
