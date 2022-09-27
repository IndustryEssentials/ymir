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

# Update items for user label files
* update ymir_version from 1.1.0 to 1.3.0
"""

import logging
import os
import tarfile
from typing import List, Set, Tuple

from google.protobuf.json_format import MessageToDict, ParseDict
import yaml

from mir.protos import mir_command_110_pb2 as mirpb110, mir_command_130_pb2 as mirpb130
from mir.tools import revs_parser
from mir.tools import mir_storage_ops_110 as mso110, mir_storage_ops_130 as mso130

from tools import get_repo_tags, remove_old_tag

_MirDatas110 = Tuple[mirpb110.MirMetadatas, mirpb110.MirAnnotations, mirpb110.Task]
_MirDatas130 = Tuple[mirpb130.MirMetadatas, mirpb130.MirAnnotations, mirpb130.Task]

_DEFAULT_STAGE_NAME = 'default_best_stage'


def update_all(mir_root: str) -> None:
    logging.info(f"updating repo: {mir_root}, 110 -> 130")

    for tag in get_repo_tags(mir_root):
        logging.info(f"    updating: {tag}")
        rev_tid = revs_parser.parse_single_arg_rev(src_rev=tag, need_tid=True)
        datas = _load(mir_root, rev_tid)
        updated_datas = _update(datas)
        _save(mir_root, rev_tid, updated_datas)


def update_user_labels(label_path: str) -> None:
    logging.info(f"updating user labels: {label_path}, 110 -> 130")

    with open(label_path, 'r') as f:
        label_contents = yaml.safe_load(f)
    label_contents['ymir_version'] = '1.3.0'
    with open(label_path, 'w') as f:
        yaml.safe_dump(label_contents, f)


def _load(mir_root: str, rev_tid: revs_parser.TypRevTid) -> _MirDatas110:
    m, a, t = mso110.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=rev_tid.rev,
        mir_task_id=rev_tid.tid,
        ms_list=[mirpb110.MIR_METADATAS, mirpb110.MIR_ANNOTATIONS, mirpb110.MIR_TASKS])
    return (m, a, t.tasks[t.head_task_id])


def _update(datas: _MirDatas110) -> _MirDatas130:
    mm110, ma110, t110 = datas
    return (_update_metadatas(mm110), _update_annotations(ma110), _update_task(t110))


def _save(mir_root: str, rev_tid: revs_parser.TypRevTid, updated_datas: _MirDatas130) -> None:
    # remove old tag
    remove_old_tag(mir_root=mir_root, tag=rev_tid.rev_tid)
    # save
    mm130, ma130, t130 = updated_datas
    mso130.MirStorageOps.save_and_commit(mir_root=mir_root,
                                         mir_branch=rev_tid.rev,
                                         his_branch=rev_tid.rev,
                                         mir_datas={
                                             mirpb130.MirStorage.MIR_METADATAS: mm130,
                                             mirpb130.MirStorage.MIR_ANNOTATIONS: ma130,
                                         },
                                         task=t130)


def _update_metadatas(mm110: mirpb110.MirMetadatas) -> mirpb130.MirMetadatas:
    mm130 = mirpb130.MirMetadatas()
    for asset_id, attr110 in mm110.attributes.items():
        attr130 = mirpb130.MetadataAttributes(tvt_type=attr110.tvt_type,
                                              asset_type=attr110.asset_type,
                                              width=attr110.width,
                                              height=attr110.height,
                                              image_channels=attr110.image_channels)

        attr130.timestamp.start = attr110.timestamp.start
        attr130.timestamp.duration = attr110.timestamp.duration

        asset_path = ''
        if os.path.isfile(os.path.join('/ymir-assets', asset_id)):
            asset_path = os.path.join('/ymir-assets', asset_id)
        elif os.path.isfile(os.path.join('/ymir-assets', asset_id[-2:], asset_id)):
            asset_path = os.path.join('/ymir-assets', asset_id[-2:], asset_id)
        attr130.byte_size = os.stat(asset_path).st_size if asset_path else 0

        mm130.attributes[asset_id].CopyFrom(attr130)
    return mm130


def _update_annotations(ma110: mirpb110.MirAnnotations) -> mirpb130.MirAnnotations:
    ta110 = ma110.task_annotations[ma110.head_task_id]

    ma130 = mirpb130.MirAnnotations()
    task_class_ids: Set[int] = set()
    for asset_id, sia110 in ta110.image_annotations.items():
        sia130 = ma130.prediction.image_annotations[asset_id]
        for anno110 in sia110.annotations:
            oa130 = mirpb130.ObjectAnnotation()
            ParseDict(MessageToDict(anno110, preserving_proto_field_name=True, use_integers_for_enums=True), oa130)
            oa130.anno_quality = -1
            oa130.cm = mirpb130.ConfusionMatrixType.NotSet
            oa130.det_link_id = -1
            sia130.boxes.append(oa130)

            task_class_ids.add(oa130.class_id)

        sia130.img_class_ids[:] = {b.class_id for b in sia130.boxes}

    ma130.prediction.task_id = ma110.head_task_id
    ma130.prediction.type = mirpb130.AnnoType.AT_DET_BOX
    ma130.prediction.task_class_ids[:] = list(task_class_ids)

    ma130.ground_truth.CopyFrom(ma130.prediction)

    return ma130


def _update_task(t110: mirpb110.Task) -> mirpb130.Task:
    t130 = mirpb130.Task(type=t110.type,
                         name=t110.name,
                         task_id=t110.task_id,
                         timestamp=t110.timestamp,
                         return_code=t110.return_code,
                         return_msg=t110.return_msg,
                         serialized_task_parameters=t110.serialized_task_parameters,
                         serialized_executor_config=t110.serialized_executor_config,
                         src_revs=t110.src_revs,
                         dst_rev=t110.dst_rev,
                         executor=t110.executor)
    for k, v in t110.unknown_types.items():
        t130.new_types[k] = v
    t130.new_types_added = (len(t130.new_types) > 0)

    # model meta
    m110 = t110.model
    if m110.model_hash:
        m130 = mirpb130.ModelMeta(model_hash=m110.model_hash,
                                  mean_average_precision=m110.mean_average_precision,
                                  context=m110.context,
                                  best_stage_name=_DEFAULT_STAGE_NAME)

        ms130 = mirpb130.ModelStage(stage_name=_DEFAULT_STAGE_NAME,
                                    mAP=m110.mean_average_precision,
                                    timestamp=t110.timestamp)
        ms130.files[:] = _get_model_file_names(m110.model_hash)
        m130.stages[_DEFAULT_STAGE_NAME].CopyFrom(ms130)

        m130.class_names[:] = _get_model_class_names(t110.serialized_executor_config)
        t130.model.CopyFrom(m130)

    # evaluation: no need to update

    return t130


def _get_model_file_names(model_hash: str) -> List[str]:
    with tarfile.open(os.path.join('/ymir-models', model_hash), 'r') as f:
        file_names = [x.name for x in f.getmembers() if x.name != 'ymir-info.yaml']
    return file_names


def _get_model_class_names(serialized_executor_config: str) -> List[str]:
    if not serialized_executor_config:
        return []

    executor_config = yaml.safe_load(serialized_executor_config)
    return executor_config.get('class_names', [])
