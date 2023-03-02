import argparse
import logging
import time
from typing import List

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import annotations, checker, exporter, mir_repo_utils, mir_storage_ops, revs_parser
from mir.tools.class_ids import load_or_create_userlabels
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter


class CmdExport(base.BaseCommand):
    def run(self) -> int:
        logging.debug(f"command export: {self.args}")

        return CmdExport.run_with_args(
            mir_root=self.args.mir_root,
            label_storage_file=self.args.label_storage_file,
            asset_dir=self.args.asset_dir,
            pred_dir=self.args.pred_dir,
            gt_dir=self.args.gt_dir,
            media_location=self.args.media_location,
            src_revs=self.args.src_revs,
            dst_rev=f"export-{self.args.src_revs}-{time.time()}",
            asset_format=exporter.parse_asset_format(self.args.asset_format),
            anno_format=annotations.parse_anno_format(self.args.anno_format),
            class_names=self.args.class_names.split(';') if self.args.class_names else [],
            work_dir=self.args.work_dir,
        )

    @staticmethod
    @command_run_in_out
    def run_with_args(
        mir_root: str,
        label_storage_file: str,
        asset_dir: str,
        pred_dir: str,
        gt_dir: str,
        media_location: str,
        src_revs: str,
        dst_rev: str,
        asset_format: "mirpb.AssetFormat.V",
        anno_format: "mirpb.ExportFormat.V",
        class_names: List[str],
        work_dir: str,
    ) -> int:
        if not asset_dir or not media_location or not src_revs:
            logging.error('empty --asset-dir, --media-location or --src-revs')
            return MirCode.RC_CMD_INVALID_ARGS

        src_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=False)

        PhaseLoggerCenter.create_phase_loggers(top_phase='export',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name='default-task')

        check_code = checker.check(mir_root, prerequisites=[checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        # prepare
        cls_mgr = load_or_create_userlabels(label_storage_file=label_storage_file)
        class_ids_list, unknown_names = cls_mgr.id_for_names(class_names)
        if unknown_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"unknown class names: {unknown_names}")
        class_ids_mapping = {class_id: class_id for class_id in class_ids_list}

        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_metadatas, mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=src_rev_tid.rev,
            mir_task_id=src_rev_tid.tid,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS])

        ec = mirpb.ExportConfig(asset_format=asset_format,
                                asset_dir=asset_dir,
                                media_location=media_location,
                                need_sub_folder=True,
                                anno_format=anno_format,
                                gt_dir=gt_dir,
                                pred_dir=pred_dir,)
        export_code = exporter.export_mirdatas_to_dir(
            mir_metadatas=mir_metadatas,
            ec=ec,
            mir_annotations=mir_annotations,
            class_ids_mapping=class_ids_mapping,
            cls_id_mgr=cls_mgr,
        )
        if export_code != MirCode.RC_OK:
            return export_code

        # add task result commit
        task = mir_storage_ops.create_task_record(task_type=mirpb.TaskType.TaskTypeExportData,
                                                  task_id=dst_rev_tid.tid,
                                                  message=f"export from {src_rev_tid.rev_tid}")
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_rev_tid.rev,
                                                      his_branch=src_rev_tid.rev,
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS:
                                                          mirpb.MirMetadatas(),
                                                          mirpb.MirStorage.MIR_ANNOTATIONS:
                                                          annotations.make_empty_mir_annotations(),
                                                      },
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
    exporting_arg_parser.add_argument("--pred-dir",
                                      required=False,
                                      dest="pred_dir",
                                      type=str,
                                      help="export directory for prediction")
    exporting_arg_parser.add_argument("--gt-dir",
                                      required=False,
                                      dest="gt_dir",
                                      type=str,
                                      help="export directory for ground-truth")
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
    exporting_arg_parser.add_argument('--anno-format',
                                      dest='anno_format',
                                      type=str,
                                      default="none",
                                      choices=["none", "det-ark", "det-voc", "det-ls-json", "seg-coco"],
                                      help='annotation format')
    exporting_arg_parser.add_argument('--asset-format',
                                      dest='asset_format',
                                      type=str,
                                      default='raw',
                                      choices=['raw', 'lmdb'],
                                      help='asset format: raw / lmdb')
    exporting_arg_parser.add_argument('--class_names',
                                      dest="class_names",
                                      type=str,
                                      required=False,
                                      default='',
                                      help="class names, do not set if you want to export all types")
    exporting_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    exporting_arg_parser.set_defaults(func=CmdExport)
