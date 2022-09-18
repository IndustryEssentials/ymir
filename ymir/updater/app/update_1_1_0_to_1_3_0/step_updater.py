
import logging

from tools import repo_walker

from ymir_1_1_0.mir.protos import mir_command_pb2 as mirpb110
from ymir_1_3_0.mir.protos import mir_command_pb2 as mirpb130


def update_all(sandbox_root: str) -> None:
    logging.info('1.1.0 -> 1.3.0')
    logging.info(f"sandbox root: {sandbox_root}")

    for mir_root, tag in repo_walker.walk(sandbox_root):
        logging.info(f"{mir_root} - {tag}")
    logging.info(f"done")
