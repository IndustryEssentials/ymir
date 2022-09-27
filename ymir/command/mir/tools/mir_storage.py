import hashlib
import os

from mir.tools.errors import MirCode, MirRuntimeError


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
