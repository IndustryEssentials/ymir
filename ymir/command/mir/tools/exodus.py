"""
use this module to read contents in other branch head ref or from other tags \n
some mir commands, such as `mir search`, `mir merge` will use this module
"""

import io
import os

from mir import scm
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def read_mir(mir_root: str, rev: str, file_name: str) -> bytes:
    if not mir_root or not file_name or not rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid args')

    scm_git = scm.Scm(mir_root if mir_root else ".", scm_executable="git")
    blob_hash = scm_git.rev_parse(f"{rev}:{file_name}")
    if not blob_hash:
        raise MirRuntimeError(MirCode.RC_CMD_INVALID_MIR_REPO, f"found no file: {rev}:{file_name}")

    bio = io.BytesIO()
    scm_git.cat_file(['-p', blob_hash], output_stream=bio)
    if not os.path.isfile(os.path.join(mir_root, '.gitattributes')) or not bio.getvalue():
        return bio.getvalue()

    cat_file_result_lines = bio.getvalue().decode('utf-8').splitlines()
    if len(cat_file_result_lines) == 3 and cat_file_result_lines[1].startswith('oid sha256:'):
        lfs_file_hash = cat_file_result_lines[1][11:]
        lfs_file_path = os.path.join(
            mir_root, '.git', 'lfs', 'objects', lfs_file_hash[:2], lfs_file_hash[2:4], lfs_file_hash)
        with open(lfs_file_path, 'rb') as f:
            return f.read()
    raise MirRuntimeError(MirCode.RC_CMD_INVALID_MIR_REPO, f"found no lfs file: {rev}:{file_name}")

    # bio2 = io.BytesIO()
    # # subprocess.run(['git', 'cat-file', '-p', blob_hash, '|', 'git', 'lfs', 'smudge'], stdout=bio2)
    # catfile_ps = subprocess.Popen(['git', 'cat-file', '-p', blob_hash], stdout=subprocess.PIPE, cwd=mir_root)
    # smudge_ps = subprocess.Popen(['git', 'lfs', 'smudge'], stdin=catfile_ps.stdout, stdout=bio2, cwd=mir_root)
    # catfile_ps.wait()
    # return bio2.getvalue()
    # bio = io.BytesIO()
    # bio2 = io.BytesIO()
    # scm_git.cat_file(['-p', blob_hash], output_stream=bio)
    # scm_git.lfs(['smudge'], istream=bio.getvalue(), output_stream=bio2)
    # return bio2.getvalue()
