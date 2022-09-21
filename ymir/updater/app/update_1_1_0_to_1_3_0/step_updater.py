
import logging

from ymir_1_1_0.mir.protos import mir_command_pb2 as mirpb110
from ymir_1_3_0.mir.protos import mir_command_pb2 as mirpb130


def update_all(mir_root: str) -> None:
    logging.info('1.1.0 -> 1.3.0')
    logging.info(f"mir root: {mir_root}")
