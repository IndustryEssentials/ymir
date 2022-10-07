import logging
import os
import re

from id_definition.task_id import IDProto
from mir.tools import revs_parser
from mir.protos import mir_command_122_pb2 as pb_src, mir_command_130_pb2 as pb_dst
from mir.tools import mir_storage_ops_122 as mso_src, mir_storage_ops_130 as mso_dst

from tools import get_repo_tags, remove_old_tag, get_model_hashes


def update_repo(mir_root: str, assets_root: str, models_root: str) -> None:
    logging.info(f"updating repo: {mir_root}, 122 -> 130")

    mir_label_file = os.path.join(mir_root, '.mir', 'labels.yaml')
    if not os.path.islink(mir_label_file):
        raise RuntimeError(f"Repo label file: {mir_label_file} is not linked to user labels")

    for tag in get_repo_tags(mir_root):
        if not re.match(f"^.{{{IDProto.ID_LENGTH}}}@.{{{IDProto.ID_LENGTH}}}$", tag):
            logging.info(f"    skip: {tag}")
            continue

        logging.info(f"    updating: {tag}")
        rev_tid = revs_parser.parse_single_arg_rev(src_rev=tag, need_tid=True)


def update_models(models_root: str) -> None:
    logging.info(f"updating models: {models_root}, 122 -> 130")
