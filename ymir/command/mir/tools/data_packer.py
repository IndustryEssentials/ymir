from enum import Enum


class PackFormat(str, Enum):
    PACK_FORMAT_UNKNOWN = 'unknown'
    PACK_FORMAT_LMDB = 'lmdb'


def pack(index_file: str,
         assets_dir: str,
         annotations_dir: str,
         format_type: PackFormat,
         export_package_path: str) -> bool:
    return True
