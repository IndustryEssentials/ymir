import argparse
import logging
import time

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, data_exporter, mir_repo_utils, mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter


class CmdExport(base.BaseCommand):
    def run(self) -> int:
        logging.debug(f"command export: {self.args}")

        dst_rev = self.args.dst_rev
        if not dst_rev:
            task_id = f"exporting-task-{float(time.time())}"
            dst_rev = f"{task_id}@{task_id}"

        return CmdExport.run_with_args(mir_root=self.args.mir_root,
                                       asset_dir=self.args.asset_dir,
                                       annotation_dir=self.args.annotation_dir,
                                       media_location=self.args.media_location,
                                       src_revs=self.args.src_revs,
                                       dst_rev=dst_rev,
                                       in_cis=self.args.in_cis,
                                       work_dir=self.args.work_dir,
                                       format=self.args.format)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, asset_dir: str, annotation_dir: str, media_location: str, src_revs: str,
                      format: str, in_cis: str, work_dir: str, dst_rev: str) -> int:
        # check args
        if not format:
            format = 'none'

        if not asset_dir or not annotation_dir or not media_location or not src_revs:
            logging.error('empty --asset-dir, --annotation-dir, --media-location or --src-revs')
            return MirCode.RC_CMD_INVALID_ARGS
        if format and (not data_exporter.check_support_format(format)):
            logging.error(f"invalid --format: {format}")
            return MirCode.RC_CMD_INVALID_ARGS

        src_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        PhaseLoggerCenter.create_phase_loggers(top_phase='export',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name='default-task')

        check_code = checker.check(mir_root, prerequisites=[checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        format_type = data_exporter.format_type_from_str(format)

        # asset ids
        mir_metadatas: mirpb.MirMetadatas = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=mir_root, mir_branch=src_rev_tid.rev, mir_task_id=src_rev_tid.tid, ms=mirpb.MIR_METADATAS)
        asset_ids = set()
        for k in mir_metadatas.attributes.keys():
            asset_ids.add(str(k))
        if not asset_ids:
            logging.error('nothing to export')
            return MirCode.RC_CMD_INVALID_ARGS

        cls_mgr = class_ids.ClassIdManager(mir_root=mir_root)
        class_names = in_cis.split(';') if in_cis else []
        type_ids_list, unknown_names = cls_mgr.id_for_names(class_names)
        if unknown_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"unknown class names: {unknown_names}")

        # export
        data_exporter.export(mir_root=mir_root,
                             assets_location=media_location,
                             class_type_ids={type_id: type_id
                                             for type_id in type_ids_list},
                             asset_ids=asset_ids,
                             asset_dir=asset_dir,
                             annotation_dir=annotation_dir,
                             need_ext=True,
                             need_id_sub_folder=False,
                             base_branch=src_rev_tid.rev,
                             base_task_id=src_rev_tid.tid,
                             format_type=format_type)

        # add task result commit
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeExportData,
                                           task_id=dst_rev_tid.tid,
                                           message=f"export from {src_rev_tid.rev_tid}")
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_rev_tid.rev,
                                                      his_branch=src_rev_tid.rev,
                                                      mir_datas={},
                                                      task=task)

        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
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
    exporting_arg_parser.add_argument("--dst-rev", required=False, dest="dst_rev", type=str, help="rev@tid")
    exporting_arg_parser.add_argument('--format',
                                      dest='format',
                                      type=str,
                                      default="none",
                                      choices=data_exporter.support_format_type(),
                                      help='annotation format: ark / voc / none')
    exporting_arg_parser.add_argument("-p",
                                      '--cis',
                                      dest="in_cis",
                                      type=str,
                                      required=False,
                                      default='',
                                      help="type names, do not set if you want to export all types")
    exporting_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    exporting_arg_parser.set_defaults(func=CmdExport)
