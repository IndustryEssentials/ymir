
import logging
import os

from common_utils import sandbox

from ymir_1_1_0.mir.protos import mir_command_pb2 as mirpb110
from ymir_1_3_0.mir.protos import mir_command_pb2 as mirpb130


def update_all(sandbox_root: str) -> None:
    logging.info('1.1.0 -> 1.3.0')

    for repo_rel_path in sandbox.get_all_repo_rel_paths(sandbox_root):
        mir_root = os.path.join(sandbox_root, repo_rel_path)
        for tag in sandbox.get_tags_for_repo(mir_root):
            _update_single_tag(mir_root=mir_root, tag=tag)
    logging.info(f"done")


def _update_single_tag(mir_root: str, tag: str) -> None:
    logging.info(f"updating: {mir_root}: {tag}")
