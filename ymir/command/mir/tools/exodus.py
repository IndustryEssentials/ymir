"""
use this module to read contents in other branch head ref or from other tags \n
some mir commands, such as `mir search`, `mir merge` will use this module
"""

import logging  # for test
import os
import zlib

from mir import scm
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def _blob_path_in_rev(mir_root: str, file_name: str, rev: str) -> str:
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

    blob_hash = scm_git.rev_parse(f"{rev}:{file_name}")
    if not blob_hash:
        raise MirRuntimeError(MirCode.RC_CMD_INVALID_MIR_REPO, f"found no file: {rev}:{file_name}")

    return os.path.join(mir_root, ".git/objects", blob_hash[:2], blob_hash[2:])


def read_mir(mir_root: str, rev: str, file_name: str) -> bytes:
    blob_path = _blob_path_in_rev(mir_root=mir_root, file_name=file_name, rev=rev)
    with open(blob_path, 'rb') as f:
        compressed_blob = f.read()
    if not compressed_blob:
        return MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                               error_message=f"empty blob: {rev}:{file_name}")

    decompressed_blob = zlib.decompress(compressed_blob)

    if decompressed_blob.startswith(b'blob 0\x00'):
        # blob with empty file
        return b''

    idx = decompressed_blob.find(b'\n')
    if idx < 0 or idx >= len(decompressed_blob):
        logging.info(f"invalid blob path: {blob_path}")
        logging.info(f"decompressed blob: {decompressed_blob}")
        logging.info(f"idx: {idx}")
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"invalid blob: {rev}:{file_name}")

    return decompressed_blob[idx:]
