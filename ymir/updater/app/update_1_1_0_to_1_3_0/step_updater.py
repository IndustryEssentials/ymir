
import logging

from tools import get_repo_tags

from update_1_1_0_to_1_3_0.mir.tools import mir_storage_ops as mso
from ymir_1_1_0.mir.protos import mir_command_pb2 as mirpb110
from ymir_1_3_0.mir.protos import mir_command_pb2 as mirpb130


def update_all(mir_root: str) -> None:
    logging.info('1.1.0 -> 1.3.0')
    logging.info(f"mir root: {mir_root}")

    for tag in get_repo_tags(mir_root):
        mir_datas = _load(mir_root, tag)
        _update(mir_datas)
        _save(mir_root, tag)


def _load(mir_root: str, tag: str) -> dict:
    pass


def _update(mir_datas: dict) -> None:
    pass


def _save(mir_root: str, tag: str, mir_datas: dict) -> None:
    pass
