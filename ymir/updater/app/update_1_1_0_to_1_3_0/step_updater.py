
import logging

from common_utils.sandbox import SandboxInfo

from .mir.tools import mir_storage_ops
from ymir_1_1_0.mir.protos import mir_command_pb2 as mirpb110
from ymir_1_3_0.mir.protos import mir_command_pb2 as mirpb130


def update_all(sandbox_info: SandboxInfo) -> None:
    logging.info('1.1.0 -> 1.3.0')
    logging.info(f"sandbox root: {sandbox_info.root}")
