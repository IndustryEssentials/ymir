"""
Updater from 1.1.0 to 1.3.0

# Update items for mir repos
* `MirMetadatas`:
    * add `byte_size` to `MetadataAttributes`
* `MirAnnotations`
    * use previous annotations as both `prediction` and `ground_truth`
* `MirTasks`:
    * create default_best_stage
    * ignore all evaluation result in previous datasets
* `MirKeywords` & `MirContext`:
    * regenerated using new data structures

"""

import logging
import os
import re
import tarfile
from typing import List, Tuple

from google.protobuf.json_format import MessageToDict, ParseDict
import yaml

from id_definition.task_id import IDProto
from mir.tools import revs_parser
from mir.protos import mir_command_110_pb2 as pb_src, mir_command_200_pb2 as pb_dst
from mir.tools import mir_storage_ops_110 as mso_src, mir_storage_ops_200 as mso_dst

from tools import get_repo_tags, remove_old_tag

_MirDatasSrc = Tuple[pb_src.MirMetadatas, pb_src.MirAnnotations, pb_src.Task]
_MirDatasDst = Tuple[pb_dst.MirMetadatas, pb_dst.MirAnnotations, pb_dst.Task]

_DEFAULT_STAGE_NAME = 'default_best_stage'
_SRC_YMIR_VER = '1.1.0'
_DST_YMIR_VER = '2.0.0'


# update user repo
def update_repo(mir_root: str, assets_root: str, models_root: str) -> None:
    logging.info(f"updating repo: {mir_root}, {_SRC_YMIR_VER} -> {_DST_YMIR_VER}")

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
    # remove old tag
    remove_old_tag(mir_root=mir_root, tag=rev_tid.rev_tid)
    # save
    mir_metadatas_dst, mir_annotations_dst, task_dst = datas_dst
    mso_dst.MirStorageOps.save_and_commit(mir_root=mir_root,
                                          mir_branch=rev_tid.rev,
                                          his_branch=rev_tid.rev,
                                          mir_datas={
                                              pb_dst.MirStorage.MIR_METADATAS: mir_metadatas_dst,
                                              pb_dst.MirStorage.MIR_ANNOTATIONS: mir_annotations_dst,
                                          },
                                          task=task_dst)


def _update_metadatas(mir_metadatas_src: pb_src.MirMetadatas, assets_root: str) -> pb_dst.MirMetadatas:
    mir_metadatas_dst = pb_dst.MirMetadatas()
    for asset_id, attr_src in mir_metadatas_src.attributes.items():
        attr_dst = pb_dst.MetadataAttributes(tvt_type=attr_src.tvt_type,
                                             asset_type=attr_src.asset_type,
                                             width=attr_src.width,
                                             height=attr_src.height,
                                             image_channels=attr_src.image_channels)

        attr_dst.timestamp.start = attr_src.timestamp.start
        attr_dst.timestamp.duration = attr_src.timestamp.duration

        asset_path = mso_dst.locate_asset_path(location=assets_root, hash=asset_id)
        attr_dst.byte_size = os.stat(asset_path).st_size if asset_path else 0

        mir_metadatas_dst.attributes[asset_id].CopyFrom(attr_dst)
    return mir_metadatas_dst


def _update_annotations(mir_annotations_src: pb_src.MirAnnotations) -> pb_dst.MirAnnotations:
    task_annotations_src = mir_annotations_src.task_annotations[mir_annotations_src.head_task_id]

    mir_annotations_dst = pb_dst.MirAnnotations()
    for asset_id, single_image_annotations_src in task_annotations_src.image_annotations.items():
        single_image_annotations_dst = mir_annotations_dst.ground_truth.image_annotations[asset_id]
        for annotation_src in single_image_annotations_src.annotations:
            object_annotation_dst = pb_dst.ObjectAnnotation()
            ParseDict(MessageToDict(annotation_src, preserving_proto_field_name=True, use_integers_for_enums=True),
                      object_annotation_dst)
            object_annotation_dst.anno_quality = -1
            object_annotation_dst.cm = pb_dst.ConfusionMatrixType.NotSet
            object_annotation_dst.det_link_id = -1
            single_image_annotations_dst.boxes.append(object_annotation_dst)

    mir_annotations_dst.ground_truth.task_id = mir_annotations_src.head_task_id
    mir_annotations_dst.ground_truth.type = pb_dst.AnnoType.AT_DET_BOX

    return mir_annotations_dst


def _update_task(task_src: pb_src.Task, models_root: str) -> pb_dst.Task:
    task_dst = pb_dst.Task(type=task_src.type,
                           name=task_src.name,
                           task_id=task_src.task_id,
                           timestamp=task_src.timestamp,
                           return_code=task_src.return_code,
                           return_msg=task_src.return_msg,
                           serialized_task_parameters=task_src.serialized_task_parameters,
                           serialized_executor_config=task_src.serialized_executor_config,
                           src_revs=task_src.src_revs,
                           dst_rev=task_src.dst_rev,
                           executor=task_src.executor)
    for k, v in task_src.unknown_types.items():
        task_dst.new_types[k] = v
    task_dst.new_types_added = (len(task_dst.new_types) > 0)

    # model meta
    model_src = task_src.model
    if model_src.model_hash:
        model_dst = pb_dst.ModelMeta(model_hash=model_src.model_hash,
                                     mean_average_precision=model_src.mean_average_precision,
                                     context=model_src.context,
                                     best_stage_name=_DEFAULT_STAGE_NAME)

        stage_dst = pb_dst.ModelStage(stage_name=_DEFAULT_STAGE_NAME,
                                      mAP=model_src.mean_average_precision,
                                      timestamp=task_src.timestamp)
        stage_dst.files[:] = _get_model_file_names(os.path.join(models_root, model_src.model_hash))
        model_dst.stages[_DEFAULT_STAGE_NAME].CopyFrom(stage_dst)

        model_dst.class_names[:] = _get_model_class_names(task_src.serialized_executor_config)
        task_dst.model.CopyFrom(model_dst)

    # evaluation: no need to update

    return task_dst


def _get_model_file_names(model_path: str) -> List[str]:
    with tarfile.open(model_path, 'r') as f:
        file_names = [x.name for x in f.getmembers() if x.name != 'ymir-info.yaml']
    return file_names


def _get_model_class_names(serialized_executor_config: str) -> List[str]:
    if not serialized_executor_config:
        return []

    executor_config = yaml.safe_load(serialized_executor_config)
    return executor_config.get('class_names', [])
