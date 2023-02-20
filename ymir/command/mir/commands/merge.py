"""
mir merge: merge contents from another guest branch to current branch
"""

import argparse
import logging
from typing import List, Tuple

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, mir_storage_ops, revs_parser
from mir.tools.annotations import exclude_from_mirdatas, merge_to_mirdatas, tvt_type_from_str, MergeStrategy
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.code import MirCode


class CmdMerge(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command merge: %s", self.args)
        return CmdMerge.run_with_args(mir_root=self.args.mir_root,
                                      src_revs=self.args.src_revs,
                                      ex_src_revs=self.args.ex_src_revs,
                                      dst_rev=self.args.dst_rev,
                                      strategy=MergeStrategy(self.args.strategy),
                                      work_dir=self.args.work_dir)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, src_revs: str, ex_src_revs: str, dst_rev: str, strategy: MergeStrategy,
                      work_dir: str) -> int:
        src_typ_rev_tids = revs_parser.parse_arg_revs(src_revs)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)
        ex_typ_rev_tids = revs_parser.parse_arg_revs(ex_src_revs) if ex_src_revs else []

        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        mir_metadatas, mir_annotations = merge_with_pb(mir_root=mir_root,
                                                       src_typ_rev_tids=src_typ_rev_tids,
                                                       ex_typ_rev_tids=ex_typ_rev_tids,
                                                       strategy=strategy)

        # create and write tasks
        task = mir_storage_ops.create_task_record(task_type=mirpb.TaskType.TaskTypeMerge,
                                                  task_id=dst_typ_rev_tid.tid,
                                                  message=f"merge: {src_revs} - {ex_src_revs} to {dst_rev}",
                                                  src_revs=src_revs,
                                                  dst_rev=dst_rev)

        mir_data = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=src_typ_rev_tids[0].rev,
                                                      mir_datas=mir_data,
                                                      task=task)

        return MirCode.RC_OK


def merge_with_pb(mir_root: str, src_typ_rev_tids: List[revs_parser.TypRevTid],
                  ex_typ_rev_tids: List[revs_parser.TypRevTid],
                  strategy: MergeStrategy) -> Tuple[mirpb.MirMetadatas, mirpb.MirAnnotations]:
    # Read host id mir data.
    host_typ_rev_tid = src_typ_rev_tids[0]

    host_mir_metadatas: mirpb.MirMetadatas
    host_mir_annotations: mirpb.MirAnnotations
    host_mir_metadatas, host_mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=host_typ_rev_tid.rev,
        mir_task_id=host_typ_rev_tid.tid,
        ms_list=[mirpb.MIR_METADATAS, mirpb.MIR_ANNOTATIONS],
        as_dict=False)

    # reset all host tvt type
    #   if not set, keep origin tvt type
    host_tvt_type = tvt_type_from_str(host_typ_rev_tid.typ)
    if host_tvt_type != mirpb.TvtType.TvtTypeUnknown:
        for asset_id in host_mir_metadatas.attributes:
            host_mir_metadatas.attributes[asset_id].tvt_type = host_tvt_type
    # associated prediction infos: remove model infos
    if len(src_typ_rev_tids) > 1:
        host_mir_annotations.prediction.model.Clear()
        host_mir_annotations.prediction.executor_config = ''

    for typ_rev_tid in src_typ_rev_tids[1:]:
        guest_mir_metadatas, guest_mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=typ_rev_tid.rev,
            mir_task_id=typ_rev_tid.tid,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS],
            as_dict=False)
        merge_to_mirdatas(host_mir_metadatas=host_mir_metadatas,
                          host_mir_annotations=host_mir_annotations,
                          guest_mir_metadatas=guest_mir_metadatas,
                          guest_mir_annotations=guest_mir_annotations,
                          guest_tvt_typ=tvt_type_from_str(typ_rev_tid.typ),
                          strategy=strategy)
        logging.info(f"Merged {typ_rev_tid.typ_rev_tid}, total assets: {len(host_mir_metadatas.attributes)}")

    for typ_rev_tid in ex_typ_rev_tids:
        guest_mir_metadatas = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=mir_root,
            mir_branch=typ_rev_tid.rev,
            mir_task_id=typ_rev_tid.tid,
            ms=mirpb.MirStorage.MIR_METADATAS)
        exclude_from_mirdatas(host_mir_metadatas=host_mir_metadatas,
                              host_mir_annotations=host_mir_annotations,
                              guest_mir_metadatas=guest_mir_metadatas)

    return (host_mir_metadatas, host_mir_annotations)


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    merge_arg_parser = subparsers.add_parser("merge",
                                             parents=[parent_parser],
                                             description="use this command to merge contents from other branch",
                                             help="merge contents from other branch")
    merge_arg_parser.add_argument("--src-revs",
                                  dest="src_revs",
                                  type=str,
                                  required=True,
                                  help="source tvt types, revs and base task ids, first the host, others the guests, "
                                  "can begin with tr:/va:/te:, uses own tvt type if no prefix assigned")
    merge_arg_parser.add_argument("--ex-src-revs",
                                  dest="ex_src_revs",
                                  type=str,
                                  help="branch(es) id, from which you want to exclude, seperated by comma.")
    merge_arg_parser.add_argument("--dst-rev",
                                  dest="dst_rev",
                                  type=str,
                                  required=True,
                                  help="rev@tid: destination branch name and task id")
    merge_arg_parser.add_argument("-s",
                                  dest="strategy",
                                  type=str,
                                  default="stop",
                                  choices=["stop", "host", "guest"],
                                  help="conflict resolvation strategy, stop (default): stop when conflict detects; "
                                  "host: use host; guest: use guest")
    merge_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    merge_arg_parser.set_defaults(func=CmdMerge)
