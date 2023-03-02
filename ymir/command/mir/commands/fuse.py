import argparse
import logging

from mir.commands import base
from mir.commands.merge import merge_with_pb
from mir.commands.filter import filter_with_pb
from mir.commands.sampling import sample_with_pb
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, mir_repo_utils, mir_storage_ops, revs_parser
from mir.tools.annotations import MergeStrategy
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.phase_logger import PhaseLoggerCenter


class CmdFuse(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command fuse: %s", self.args)
        return CmdFuse.run_with_args(mir_root=self.args.mir_root,
                                     src_revs=self.args.src_revs,
                                     ex_src_revs=self.args.ex_src_revs,
                                     strategy=MergeStrategy(self.args.strategy),
                                     label_storage_file=self.args.label_storage_file,
                                     in_cis=self.args.in_cis,
                                     ex_cis=self.args.ex_cis,
                                     count=self.args.count,
                                     rate=self.args.rate,
                                     dst_rev=self.args.dst_rev,
                                     work_dir=self.args.work_dir)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, src_revs: str, ex_src_revs: str, strategy: MergeStrategy, label_storage_file: str,
                      in_cis: str, ex_cis: str, count: int, rate: float, dst_rev: str, work_dir: str) -> int:
        src_typ_rev_tids = revs_parser.parse_arg_revs(src_revs)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)
        ex_typ_rev_tids = revs_parser.parse_arg_revs(ex_src_revs) if ex_src_revs else []

        PhaseLoggerCenter.create_phase_loggers(top_phase='fuse',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name=dst_typ_rev_tid.tid)

        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        mir_metadatas, mir_annotations = merge_with_pb(mir_root=mir_root,
                                                       src_typ_rev_tids=src_typ_rev_tids,
                                                       ex_typ_rev_tids=ex_typ_rev_tids,
                                                       strategy=strategy)
        PhaseLoggerCenter.update_phase(phase="fuse.merge")
        filter_with_pb(mir_metadatas=mir_metadatas,
                       mir_annotations=mir_annotations,
                       label_storage_file=label_storage_file,
                       in_cis=in_cis,
                       ex_cis=ex_cis)
        PhaseLoggerCenter.update_phase(phase="fuse.filter")
        sample_with_pb(mir_metadatas=mir_metadatas,
                       mir_annotations=mir_annotations,
                       count=count,
                       rate=rate)
        PhaseLoggerCenter.update_phase(phase="fuse.sample")

        # create and write tasks
        message = (f"merge in: {src_revs}, ex: {ex_src_revs}; sample count: {count}, rate: {rate}; "
                   f"filter in: {in_cis}, ex: {ex_cis}")
        task = mir_storage_ops.create_task_record(task_type=mirpb.TaskType.TaskTypeFusion,
                                                  task_id=dst_typ_rev_tid.tid,
                                                  message=message,
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


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    fuse_arg_parser = subparsers.add_parser("fuse",
                                            parents=[parent_parser],
                                            description="use this command to merge, filter and sample assets",
                                            help="merge, filter and sample assets")
    fuse_arg_parser.add_argument("--src-revs",
                                 dest="src_revs",
                                 type=str,
                                 required=True,
                                 help="source tvt types, revs and base task ids, first the host, others the guests, "
                                 "can begin with tr:/va:/te:, uses own tvt type if no prefix assigned")
    fuse_arg_parser.add_argument("--ex-src-revs",
                                 dest="ex_src_revs",
                                 type=str,
                                 default='',
                                 help="branch(es) id, from which you want to exclude, seperated by comma.")
    fuse_arg_parser.add_argument("-s",
                                 dest="strategy",
                                 type=str,
                                 default="stop",
                                 choices=["stop", "host", "guest"],
                                 help="conflict resolvation strategy, stop (default): stop when conflict detects; "
                                 "host: use host; guest: use guest")
    fuse_arg_parser.add_argument('--cis', dest="in_cis", type=str, default='', help="type names")
    fuse_arg_parser.add_argument('--ex-cis', dest="ex_cis", type=str, default='', help="exclusive type names")
    sampling_group = fuse_arg_parser.add_mutually_exclusive_group(required=False)
    sampling_group.add_argument('--count', dest='count', type=int, default=0, help='assets count')
    sampling_group.add_argument('--rate', dest='rate', type=float, default=0.0, help='assets sampling rate')
    fuse_arg_parser.add_argument("--dst-rev", dest="dst_rev", type=str, help="rev@tid")
    fuse_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    fuse_arg_parser.set_defaults(func=CmdFuse)
