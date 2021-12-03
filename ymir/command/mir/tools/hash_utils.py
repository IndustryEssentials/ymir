import hashlib


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


def md5sum_for_file(file_path: str) -> str:
    """
    get md5sum for file, raises FileNotFoundError if file not found
    """
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        chunk = b'0'
        while chunk != b'':
            chunk = f.read(h.block_size)
            h.update(chunk)
    return h.hexdigest()
