import logging
from typing import Tuple
from mir.tools import revs_parser

from tools import get_repo_tags

from ymir_1_1_0.mir.tools import mir_storage_ops as mso110
from ymir_1_1_0.mir.protos import mir_command_pb2 as mirpb110
from ymir_1_3_0.mir.tools import mir_storage_ops as mso130
from ymir_1_3_0.mir.protos import mir_command_pb2 as mirpb130


_MirDatas110 = Tuple[mirpb110.MirMetadatas, mirpb110.MirAnnotations, mirpb110.MirTasks]
_MirDatas130 = Tuple[mirpb130.MirMetadatas, mirpb130.MirAnnotations, mirpb130.MirTasks]


def update_all(mir_root: str) -> None:
    logging.info(f"updating repo: {mir_root}, 110 -> 130")

    for tag in get_repo_tags(mir_root):
        logging.info(f"    {tag}")

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
    m110, a110, t110 = datas

    # update mir_metadatas
    
    # update mir_annotations
    # update mir_tasks


def _save(mir_root: str, rev_tid: revs_parser.TypRevTid, updated_datas: _MirDatas130) -> None:
    pass
