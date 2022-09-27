import logging
import os
import re
from typing import Set, Tuple

from google.protobuf.json_format import MessageToDict, ParseDict

from mir.protos import mir_command_110_pb2 as mirpb110, mir_command_130_pb2 as mirpb130
from mir.tools import revs_parser
from mir.tools import mir_storage_ops_110 as mso110, mir_storage_ops_130 as mso130

from tools import get_repo_tags


_MirDatas110 = Tuple[mirpb110.MirMetadatas, mirpb110.MirAnnotations, mirpb110.MirTasks]
_MirDatas130 = Tuple[mirpb130.MirMetadatas, mirpb130.MirAnnotations, mirpb130.MirTasks]


def update_all(mir_root: str) -> None:
    logging.info(f"updating repo: {mir_root}, 110 -> 130")

    for tag in get_repo_tags(mir_root):
        if re.match(pattern=r'^t.{29}@t.{29}$', string=tag) == None:
            logging.info(f"    skip: {tag}")
            continue

        logging.info(f"    updating: {tag}")
        rev_tid = revs_parser.parse_single_arg_rev(src_rev=tag, need_tid=True)
        datas = _load(mir_root, rev_tid)
        updated_datas = _update(datas)
        _save(mir_root, rev_tid, updated_datas)


def _load(mir_root: str, rev_tid: revs_parser.TypRevTid) -> _MirDatas110:
    return mso110.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=rev_tid.rev,
        mir_task_id=rev_tid.tid,
        ms_list=[mirpb110.MIR_METADATAS, mirpb110.MIR_ANNOTATIONS, mirpb110.MIR_TASKS])


def _update(datas: _MirDatas110) -> _MirDatas130:
    mm110, ma110, mt110 = datas
    return (_update_metadatas(mm110), _update_annotations(ma110), _update_tasks(mt110))


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


def _update_tasks(mt110: mirpb110.MirTasks) -> mirpb130.MirTasks:
    mt130 = mirpb130.MirTasks()
    return mt130


def _save(mir_root: str, rev_tid: revs_parser.TypRevTid, updated_datas: _MirDatas130) -> None:
    pass
