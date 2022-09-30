import hashlib
import os
from typing import Any, List

from mir.protos import mir_command_pb2 as mirpb
from mir.tools.errors import MirCode, MirRuntimeError


MIR_ASSOCIATED_FILES = ['.git', '.gitattributes', '.gitignore', '.mir', '.mir_lock']


def mir_type(mir_storage: 'mirpb.MirStorage.V') -> Any:
    MIR_TYPE = {
        mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas,
        mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations,
        mirpb.MirStorage.MIR_KEYWORDS: mirpb.MirKeywords,
        mirpb.MirStorage.MIR_TASKS: mirpb.MirTasks,
        mirpb.MirStorage.MIR_CONTEXT: mirpb.MirContext,
    }
    return MIR_TYPE[mir_storage]


def mir_path(mir_storage: 'mirpb.MirStorage.V') -> str:
    MIR_PATH = {
        mirpb.MirStorage.MIR_METADATAS: 'metadatas.mir',
        mirpb.MirStorage.MIR_ANNOTATIONS: 'annotations.mir',
        mirpb.MirStorage.MIR_KEYWORDS: 'keywords.mir',
        mirpb.MirStorage.MIR_TASKS: 'tasks.mir',
        mirpb.MirStorage.MIR_CONTEXT: 'context.mir',
    }
    return MIR_PATH[mir_storage]


def get_all_mir_paths() -> List[str]:
    return [mir_path(ms) for ms in get_all_mir_storage()]


def get_all_mir_storage() -> List['mirpb.MirStorage.V']:
    return [
        mirpb.MirStorage.MIR_METADATAS,
        mirpb.MirStorage.MIR_ANNOTATIONS,
        mirpb.MirStorage.MIR_KEYWORDS,
        mirpb.MirStorage.MIR_TASKS,
        mirpb.MirStorage.MIR_CONTEXT,
    ]


# assets
def locate_asset_path(location: str, hash: str) -> str:
    asset_path = get_asset_storage_path(location=location, hash=hash, make_dirs=False, need_sub_folder=True)
    if os.path.isfile(asset_path):
        return asset_path

    asset_path = get_asset_storage_path(location=location, hash=hash, make_dirs=False, need_sub_folder=False)
    if os.path.isfile(asset_path):
        return asset_path

    raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message=f"cannot locate asset: {hash}")


def get_asset_storage_path(location: str, hash: str, make_dirs: bool = True, need_sub_folder: bool = True) -> str:
    if not need_sub_folder:
        return os.path.join(location, hash)

    sub_dir = os.path.join(location, hash[-2:])
    if make_dirs:
        os.makedirs(sub_dir, exist_ok=True)
    return os.path.join(sub_dir, hash)


def sha1sum_for_file(file_path: str) -> str:
    """
    get sha1sum for file, raises FileNotFoundError if file not found
    """
    h = hashlib.sha1()
    with open(file_path, "rb") as f:
        chunk = b'0'
        while chunk != b'':
            chunk = f.read(h.block_size)
            h.update(chunk)
    return h.hexdigest()
