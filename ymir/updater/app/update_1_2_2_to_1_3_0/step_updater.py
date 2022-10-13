import logging
import os
import re
import shutil
import tarfile
from typing import Tuple

from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import DecodeError
import yaml

from id_definition.task_id import IDProto
from mir.tools import revs_parser, models
from mir.protos import mir_command_122_pb2 as pb_src, mir_command_130_pb2 as pb_dst
from mir.tools import mir_storage_ops_122 as mso_src, mir_storage_ops_130 as mso_dst
from mir.version import ymir_model_salient_version, DEFAULT_YMIR_SRC_VERSION

from tools import get_repo_tags, remove_old_tag, get_model_hashes, get_model_class_names


_MirDatasSrc = Tuple[pb_src.MirMetadatas, pb_src.MirAnnotations, pb_src.Task]
_MirDatasDst = Tuple[pb_dst.MirMetadatas, pb_dst.MirAnnotations, pb_dst.Task]

_DST_YMIR_VER = '1.3.0'


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
        if tag[32] != '0':
            logging.info(f"    skip: {tag}, middle step")
            remove_old_tag(mir_root=mir_root, tag=tag)
            continue

        logging.info(f"    updating: {tag}")
        rev_tid = revs_parser.parse_single_arg_rev(src_rev=tag, need_tid=True)
        datas_src = _load(mir_root, rev_tid)
        if datas_src is None:
            continue
        logging.info('    loaded')
        datas_dst = _update(datas_src, assets_root, models_root)
        _save(mir_root, rev_tid, datas_dst)


def _load(mir_root: str, rev_tid: revs_parser.TypRevTid) -> _MirDatasSrc:
    try:
        m, a, t = mso_src.MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=rev_tid.rev,
            mir_task_id=rev_tid.tid,
            ms_list=[pb_src.MIR_METADATAS, pb_src.MIR_ANNOTATIONS, pb_src.MIR_TASKS])
        return (m, a, t.tasks[t.head_task_id])
    except DecodeError as e:
        logging.warning(f"skip: {rev_tid.rev_tid}, {e}")
        remove_old_tag(mir_root=mir_root, tag=rev_tid.rev_tid)
        return None


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
                                             image_channels=attr_src.image_channels,
                                             byte_size=attr_src.byte_size)
        attr_dst.timestamp.start = attr_src.timestamp.start
        attr_dst.timestamp.duration = attr_src.timestamp.duration

        mir_metadatas_dst.attributes[asset_id].CopyFrom(attr_dst)
    logging.info(f"    updated mir_metadatas, assets: {len(mir_metadatas_dst.attributes)}")
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

    logging.info(f"    updated mir_annotations, gt: {len(mir_annotations_dst.ground_truth.image_annotations)}, "
                 f"prediction: {len(mir_annotations_dst.prediction.image_annotations)}")
    return mir_annotations_dst


def _update_task(task_src: pb_src.Task, models_root: str) -> pb_dst.Task:
    task_dst = pb_dst.Task(type=task_src.type,
                           name=task_src.name,
                           task_id=task_src.task_id,
                           timestamp=task_src.timestamp,
                           return_code=task_src.return_code,
                           return_msg=task_src.return_msg,
                           new_types_added=task_src.new_types_added,
                           serialized_task_parameters=task_src.serialized_task_parameters,
                           serialized_executor_config=task_src.serialized_executor_config,
                           src_revs=task_src.src_revs,
                           dst_rev=task_src.dst_rev,
                           executor=task_src.executor)
    for k, v in task_src.new_types.items():
        task_dst.new_types[k] = v

    # model
    if task_src.model.model_hash:
        model_src = task_src.model
        model_dst = task_dst.model
        ParseDict(MessageToDict(model_src, preserving_proto_field_name=True, use_integers_for_enums=True),
                  model_dst,
                  ignore_unknown_fields=True)
        model_dst.class_names[:] = get_model_class_names(task_src.serialized_executor_config)

    # evaluations: no need to update
    logging.info('    updated task')
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
    model_work_dir = os.path.join(models_root, 'work_dir')

    for model_hash in get_model_hashes(models_root):
        logging.info(f"model hash: {model_hash}")

        if os.path.isdir(model_work_dir):
            shutil.rmtree(model_work_dir)
        os.makedirs(model_work_dir, exist_ok=False)

        model_path = os.path.join(models_root, model_hash)

        # extract
        with tarfile.open(model_path, 'r') as f:
            f.extractall(model_work_dir)

        os.remove(model_path)
        with open(os.path.join(model_work_dir, 'ymir-info.yaml'), 'r') as f:
            ymir_info = yaml.safe_load(f.read())
        _check_model(ymir_info)

        # check model producer version
        package_version = ymir_info.get('package_version', DEFAULT_YMIR_SRC_VERSION)
        if ymir_model_salient_version(package_version) == ymir_model_salient_version(_DST_YMIR_VER):
            logging.info('  no need to update, skip')
            continue

        # update ymir-info.yaml
        ymir_info['package_version'] = _DST_YMIR_VER

        # pack again
        model_storage = models.ModelStorage.parse_obj(ymir_info)
        new_model_hash = models.pack_and_copy_models(model_storage=model_storage,
                                                     model_dir_path=model_work_dir,
                                                     model_location=model_work_dir)  # avoid hash conflict
        shutil.move(os.path.join(model_work_dir, new_model_hash), model_path)

    # cleanup
    shutil.rmtree(model_work_dir)


def _check_model(ymir_info: dict) -> None:
    # `executor_config` and `stages` should be dict
    executor_config = ymir_info['executor_config']
    stages = ymir_info['stages']
    if not executor_config or not isinstance(executor_config, dict) or not stages or not isinstance(stages, dict):
        raise ValueError('Invalid ymir-info.yaml for model version 1.2.2')
