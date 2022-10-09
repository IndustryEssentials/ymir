import logging
import os
import re
from typing import Tuple

from google.protobuf.json_format import MessageToDict, ParseDict

from id_definition.task_id import IDProto
from mir.tools import revs_parser
from mir.protos import mir_command_122_pb2 as pb_src, mir_command_130_pb2 as pb_dst
from mir.tools import mir_storage_ops_122 as mso_src, mir_storage_ops_130 as mso_dst

from tools import get_repo_tags, remove_old_tag, get_model_hashes

_MirDatasSrc = Tuple[pb_src.MirMetadatas, pb_src.MirAnnotations, pb_src.Task]
_MirDatasDst = Tuple[pb_dst.MirMetadatas, pb_dst.MirAnnotations, pb_dst.Task]


# update user repo
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
        datas_src = _load(mir_root, rev_tid)
        datas_dst = _update(datas_src, assets_root, models_root)
        _save(mir_root, rev_tid, datas_dst)


def _load(mir_root: str, rev_tid: revs_parser.TypRevTid) -> _MirDatasSrc:
    m, a, t = mso_src.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=rev_tid.rev,
        mir_task_id=rev_tid.tid,
        ms_list=[pb_src.MIR_METADATAS, pb_src.MIR_ANNOTATIONS, pb_src.MIR_TASKS])
    return (m, a, t.tasks[t.head_task_id])


def _update(datas_src: _MirDatasSrc, assets_root: str, models_root: str) -> _MirDatasDst:
    mir_metadatas_src, mir_annotations_src, task_src = datas_src
    return (_update_metadatas(mir_metadatas_src, assets_root), _update_annotations(mir_annotations_src),
            _update_task(task_src, models_root))


def _save(mir_root: str, rev_tid: revs_parser.TypRevTid, datas_dst: _MirDatasDst) -> None:
    pass


def _update_metadatas(mir_metadatas_src: pb_src.MirMetadatas, assets_root: str) -> pb_dst.MirMetadatas:
    mir_metadatas_dst = pb_dst.MirMetadatas()
    ParseDict(MessageToDict(mir_metadatas_src, preserving_proto_field_name=True, use_integers_for_enums=True),
              mir_metadatas_dst)
    return mir_metadatas_dst


def _update_annotations(mir_annotations_src: pb_src.MirAnnotations) -> pb_dst.MirAnnotations:
    mir_annotations_dst = pb_dst.MirAnnotations()
    ParseDict(MessageToDict(mir_annotations_src, preserving_proto_field_name=True, use_integers_for_enums=True),
              mir_annotations_dst)
    mir_annotations_dst.prediction.type = pb_dst.AnnoType.AT_DET_BOX
    mir_annotations_dst.ground_truth.type = pb_dst.AnnoType.AT_DET_BOX
    return mir_annotations_dst


def _update_task(task_src: pb_src.Task, models_root: str) -> pb_dst.Task:
    task_dst = pb_dst.Task()
    return task_dst


def update_models(models_root: str) -> None:
    logging.info(f"updating models: {models_root}, 122 -> 130")


# MetadataAttributes:
# 	remove: dataset_name
# 	add: origin_filename = empty

# MirAnnotations:
# 	remove: head_task_id

# SingleTaskAnnotations:
# 	add: type = AnnoType.AT_DET_BOX
# 	add: task_class_ids = empty
# 	add: map_id_color = empty
# 	add: eval_class_ids = empty
# 	add: model = empty
# 	add: executor_config = empty

# SingleImageAnnotations:
# 	move: annotations -> boxes
# 	add: polygons = empty
# 	add: mask = empty
# 	add: img_class_ids = empty

# Annotation:
# 	add: class_name = empty
# 	add: polygon = empty

# ModelMeta:
# 	add: class_names = (from serialized executor config)

# Evaluation: no need to update
# EvaluateConfig: no need to update