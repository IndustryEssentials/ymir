import argparse
import logging
import time

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, data_exporter, mir_repo_utils, mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.phase_logger import PhaseLoggerCenter


class CmdExport(base.BaseCommand):
    def run(self) -> int:
        logging.debug(f"command export: {self.args}")

        dst_rev = self.args.dst_rev
        if not dst_rev:
            task_id = f"exporting-task-{int(time.time())}"
            dst_rev = f"{task_id}@{task_id}"

        return CmdExport.run_with_args(mir_root=self.args.mir_root,
                                       asset_dir=self.args.asset_dir,
                                       annotation_dir=self.args.annotation_dir,
                                       media_location=self.args.media_location,
                                       src_revs=self.args.src_revs,
                                       dst_rev=dst_rev,
                                       work_dir=self.args.work_dir,
                                       format=self.args.format)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str,
                      asset_dir: str,
                      annotation_dir: str,
                      media_location: str,
                      src_revs: str,
                      format: str,
                      work_dir: str,
                      dst_rev: str) -> int:
        # check args
        if not format:
            format = 'none'

        if not asset_dir or not annotation_dir:
            logging.error('empty --asset-dir or --annotation-dir')
            return MirCode.RC_CMD_INVALID_ARGS
        if not media_location:
            logging.error('empty --media-location')
            return MirCode.RC_CMD_INVALID_ARGS
        if not src_revs:
            logging.error('empty --src-revs')
            return MirCode.RC_CMD_INVALID_ARGS
        if format and (not data_exporter.check_support_format(format)):
            logging.error(f"invalid --format: {format}")
            return MirCode.RC_CMD_INVALID_ARGS

        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
        if checker.check_src_revs(src_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS

        PhaseLoggerCenter.create_phase_loggers(top_phase='export',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name='default-task')

        check_code = checker.check(mir_root, prerequisites=[checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        format_type = data_exporter.format_type_from_str(format)

        # asset ids
        mir_metadatas: mirpb.MirMetadatas = mir_storage_ops.MirStorageOps.load_single(mir_root=mir_root,
                                                                                      mir_branch=src_typ_rev_tid.rev,
                                                                                      mir_task_id=src_typ_rev_tid.tid,
                                                                                      ms=mirpb.MIR_METADATAS)
        asset_ids = set()
        for k in mir_metadatas.attributes.keys():
            asset_ids.add(str(k))
        if not asset_ids:
            logging.error('nothing to export')
            return MirCode.RC_CMD_INVALID_ARGS

        # export
        data_exporter.export(mir_root=mir_root,
                             assets_location=media_location,
                             class_type_ids={},
                             asset_ids=asset_ids,
                             asset_dir=asset_dir,
                             annotation_dir=annotation_dir,
                             need_ext=True,
                             need_id_sub_folder=False,
                             base_branch=src_typ_rev_tid.rev,
                             base_task_id=src_typ_rev_tid.tid,
                             format_type=format_type)

        # add task result commit
        CmdExport._commit(mir_root=mir_root, src_revs=src_revs, dst_rev=dst_rev)

        return MirCode.RC_OK

    @staticmethod
    def _commit(mir_root: str, src_revs: str, dst_rev: str) -> None:
        src_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
        dst_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)

        task = mirpb.Task()
        task.return_code = MirCode.RC_OK
        task.type = mirpb.TaskTypeExportData
        task.task_id = dst_rev_tid.tid
        task.timestamp = int(time.time())
        task.name = dst_rev_tid.tid

        mir_tasks = mirpb.MirTasks()
        mir_tasks.head_task_id = dst_rev_tid.tid
        mir_tasks.tasks[dst_rev_tid.tid].CopyFrom(task)

        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_rev_tid.rev,
                                                      task_id=dst_rev_tid.tid,
                                                      his_branch=src_rev_tid.rev,
                                                      mir_datas={mirpb.MIR_TASKS: mir_tasks},
                                                      commit_message=task.name)


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    exporting_arg_parser = subparsers.add_parser('export',
                                                 parents=[parent_parser],
                                                 description='use this command to export data',
                                                 help='export data')
    exporting_arg_parser.add_argument("--asset-dir",
                                      required=True,
                                      dest="asset_dir",
                                      type=str,
                                      help="export directory for assets")
    exporting_arg_parser.add_argument("--annotation-dir",
                                      required=True,
                                      dest="annotation_dir",
                                      type=str,
                                      help="export directory for annotations")
    exporting_arg_parser.add_argument('--media-location',
                                      required=True,
                                      dest='media_location',
                                      type=str,
                                      help='location of hashed assets')
    exporting_arg_parser.add_argument('--src-revs',
                                      required=True,
                                      dest='src_revs',
                                      type=str,
                                      help='rev@bid: source rev and base task id')
    exporting_arg_parser.add_argument("--dst-rev",
                                      required=False,
                                      dest="dst_rev",
                                      type=str,
                                      help="rev@tid")
    exporting_arg_parser.add_argument('--format',
                                      dest='format',
                                      type=str,
                                      default="none",
                                      choices=data_exporter.support_format_type(),
                                      help='annotation format: ark / voc / none')
    exporting_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    exporting_arg_parser.set_defaults(func=CmdExport)
