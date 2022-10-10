import logging
import os
import re
from typing import Tuple

from google.protobuf.json_format import MessageToDict, ParseDict

from id_definition.task_id import IDProto
from mir.tools import revs_parser
from mir.protos import mir_command_122_pb2 as pb_src, mir_command_130_pb2 as pb_dst
from mir.tools import mir_storage_ops_122 as mso_src, mir_storage_ops_130 as mso_dst

from tools import get_repo_tags, remove_old_tag, get_model_hashes, get_model_class_names

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
    for asset_id, attr_src in mir_metadatas_src.attributes.items():
        attr_dst = pb_dst.MetadataAttributes(tvt_type=attr_src.tvt_type,
                                             asset_type=attr_src.asset_type,
                                             width=attr_src.width,
                                             height=attr_src.height,
                                             image_channels=attr_src.image_channels,
                                             byte_size=attr_src.byte_size)
        attr_dst.timestamp.start = attr_src.timestamp.start
        attr_dst.timestamp.duration = attr_src.timestamp.duration

        mir_metadatas_dst.attributes[asset_id].CopyFrom(attr_dst)
    return mir_metadatas_dst


def _update_annotations(mir_annotations_src: pb_src.MirAnnotations) -> pb_dst.MirAnnotations:
    mir_annotations_dst = pb_dst.MirAnnotations()

    # prediction and ground_truth
    _update_task_annotations(task_annotations_src=mir_annotations_src.prediction,
                             task_annotations_dst=mir_annotations_dst.prediction)
    _update_task_annotations(task_annotations_src=mir_annotations_src.ground_truth,
                             task_annotations_dst=mir_annotations_dst.ground_truth)

    # image_cks
    for asset_id, single_image_cks_src in mir_annotations_src.image_cks.items():
        single_image_cks_dst = mir_annotations_dst.image_cks[asset_id]

        for k, v in single_image_cks_src.cks.items():
            single_image_cks_dst.cks[k] = v
        single_image_cks_dst.image_quality = single_image_cks_src.image_quality

    return mir_annotations_dst


def _update_task(task_src: pb_src.Task, models_root: str) -> pb_dst.Task:
    task_dst = pb_dst.Task()
    ParseDict(MessageToDict(task_src, preserving_proto_field_name=True, use_integers_for_enums=True), task_dst)
    if task_src.model.model_hash:
        task_dst.model.class_names[:] = get_model_class_names(task_src.serialized_executor_config)
    return task_dst


def _update_task_annotations(task_annotations_src: pb_src.SingleTaskAnnotations,
                             task_annotations_dst: pb_dst.SingleTaskAnnotations) -> None:
    task_annotations_dst.type = pb_dst.AnnoType.AT_DET_BOX
    task_annotations_dst.task_id = task_annotations_src.task_id
    for asset_id, single_image_annotations_src in task_annotations_src.image_annotations.items():
        single_image_annotations_dst = task_annotations_dst.image_annotations[asset_id]
        for annotation_src in single_image_annotations_src.annotations:
            object_annotation_dst = pb_dst.ObjectAnnotation()
            ParseDict(MessageToDict(annotation_src, preserving_proto_field_name=True, use_integers_for_enums=True),
                      object_annotation_dst)
            single_image_annotations_dst.boxes.append(object_annotation_dst)


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