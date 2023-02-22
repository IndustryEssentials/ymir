import argparse
import logging
import os
import shutil
from typing import Dict

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import annotations, checker, metadatas
from mir.tools import mir_repo_utils, mir_storage_ops, revs_parser, settings
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.tools.mir_storage import get_asset_storage_path, sha1sum_for_file


class CmdImport(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command import: %s", self.args)

        return CmdImport.run_with_args(mir_root=self.args.mir_root,
                                       label_storage_file=self.args.label_storage_file,
                                       index_file=self.args.index_file,
                                       pred_abs=self.args.pred_abs,
                                       gt_abs=self.args.gt_abs,
                                       gen_abs=self.args.gen_abs,
                                       dst_rev=self.args.dst_rev,
                                       src_revs=self.args.src_revs or 'master',
                                       work_dir=self.args.work_dir,
                                       unknown_types_strategy=annotations.UnknownTypesStrategy(
                                           self.args.unknown_types_strategy),
                                       anno_type=annotations.parse_anno_type(self.args.anno_type),
                                       is_instance_segmentation=self.args.is_instance_segmentation)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, index_file: str, pred_abs: str, gt_abs: str, gen_abs: str,
                      dst_rev: str, src_revs: str, work_dir: str, label_storage_file: str,
                      unknown_types_strategy: annotations.UnknownTypesStrategy, anno_type: "mirpb.ObjectType.V",
                      is_instance_segmentation: bool) -> int:
        # Step 1: check args and prepare environment.
        if not index_file or not gen_abs or not os.path.isfile(index_file):
            logging.error(f"invalid index_file: {index_file} or gen_abs: {gen_abs}")
            return MirCode.RC_CMD_INVALID_ARGS
        if pred_abs and not os.path.isdir(pred_abs):
            logging.error(f"prediction dir invalid: {pred_abs}")
            return MirCode.RC_CMD_INVALID_ARGS
        if gt_abs and not os.path.isdir(gt_abs):
            logging.error(f"groundtruth dir invalid: {gt_abs}")
            return MirCode.RC_CMD_INVALID_ARGS
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)

        PhaseLoggerCenter.create_phase_loggers(top_phase='import',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name=dst_typ_rev_tid.tid)

        check_code = checker.check(mir_root,
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        PhaseLoggerCenter.update_phase(phase="import.init")

        # Step 2: generate sha1 file and rename images.
        # sha1 file to be written.
        file_name_to_asset_ids = _generate_sha_and_copy(index_file, gen_abs)

        # Step 3 import metadat and annotations:
        mir_metadatas = mirpb.MirMetadatas()
        ret = metadatas.import_metadatas(mir_metadatas=mir_metadatas,
                                         file_name_to_asset_ids=file_name_to_asset_ids,
                                         hashed_asset_root=gen_abs,
                                         phase='import.metadatas')
        if ret != MirCode.RC_OK:
            logging.error(f"import metadatas error: {ret}")
            return ret

        mir_annotation = mirpb.MirAnnotations()
        unknown_class_names = annotations.import_annotations(mir_annotation=mir_annotation,
                                                             label_storage_file=label_storage_file,
                                                             prediction_dir_path=pred_abs,
                                                             groundtruth_dir_path=gt_abs,
                                                             file_name_to_asset_ids=file_name_to_asset_ids,
                                                             unknown_types_strategy=unknown_types_strategy,
                                                             anno_type=anno_type,
                                                             is_instance_segmentation=is_instance_segmentation,
                                                             phase='import.others')

        logging.info(f"pred / gt import unknown result: {unknown_class_names}")

        # create and write tasks
        task = mir_storage_ops.create_task_record(
            task_type=mirpb.TaskTypeImportData,
            task_id=dst_typ_rev_tid.tid,
            message=f"importing {index_file}-{pred_abs}-{gt_abs} to {dst_rev}, uts: {unknown_types_strategy}",
            new_types=unknown_class_names,
            new_types_added=(unknown_types_strategy == annotations.UnknownTypesStrategy.ADD),
            src_revs=src_revs,
            dst_rev=dst_rev,
        )

        mir_data = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotation,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      his_branch=src_typ_rev_tid.rev,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      mir_datas=mir_data,
                                                      task=task)

        return MirCode.RC_OK


def _generate_sha_and_copy(index_file: str, sha_folder: str) -> Dict[str, str]:
    hash_phase_name = 'import.hash'
    os.makedirs(sha_folder, exist_ok=True)

    with open(index_file) as idx_f:
        lines = idx_f.readlines()
    total_count = len(lines)
    if total_count > settings.ASSET_LIMIT_PER_DATASET:  # large number of images may trigger redis timeout error.
        raise MirRuntimeError(
            error_code=MirCode.RC_CMD_INVALID_ARGS,
            error_message=f'# of image {total_count} exceeds upper boundary {settings.ASSET_LIMIT_PER_DATASET}.')

    idx = 0
    copied_assets = 0
    asset_id_to_file_names = {}
    for line in lines:
        components = line.strip().split('\t')
        if not components:
            continue
        media_src = components[0]
        if not os.path.isfile(media_src):
            continue

        try:
            sha1 = sha1sum_for_file(media_src)
        except OSError:
            logging.info(f"{media_src} is not accessable.")
            continue

        if sha1 not in asset_id_to_file_names:
            asset_id_to_file_names[sha1] = os.path.basename(media_src)
            media_dst = get_asset_storage_path(location=sha_folder, hash=sha1)
            if not os.path.isfile(media_dst):
                copied_assets += 1
                shutil.copyfile(media_src, media_dst)

        idx += 1
        if idx % 5000 == 0:
            PhaseLoggerCenter.update_phase(phase=hash_phase_name, local_percent=(idx / total_count))
            logging.info(f"finished {idx} / {total_count} hashes")

    logging.info(f"skipped assets: {len(lines) - len(asset_id_to_file_names)}, copied assets: {copied_assets}")

    PhaseLoggerCenter.update_phase(phase=hash_phase_name)
    return {name: asset_id for asset_id, name in asset_id_to_file_names.items()}


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    import_dataset_arg_parser = subparsers.add_parser(
        "import",
        parents=[parent_parser],
        description="use this command to import data from img/anno folder",
        help="import raw data",
        formatter_class=argparse.RawTextHelpFormatter)
    import_dataset_arg_parser.add_argument("--index-file",
                                           dest="index_file",
                                           required=True,
                                           type=str,
                                           help="index of input media, one file per line")
    import_dataset_arg_parser.add_argument("--pred-dir",
                                           dest="pred_abs",
                                           type=str,
                                           required=False,
                                           help="corresponding prediction folder")
    import_dataset_arg_parser.add_argument("--gt-dir",
                                           dest="gt_abs",
                                           type=str,
                                           required=False,
                                           help="corresponding ground-truth folder")
    import_dataset_arg_parser.add_argument("--gen-dir",
                                           dest="gen_abs",
                                           required=True,
                                           type=str,
                                           help="storage path of generated data files")
    import_dataset_arg_parser.add_argument("--src-revs", dest="src_revs", type=str, help="rev: source rev")
    import_dataset_arg_parser.add_argument("--dst-rev",
                                           dest="dst_rev",
                                           type=str,
                                           required=True,
                                           help="rev@tid: destination branch name and task id")
    import_dataset_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    import_dataset_arg_parser.add_argument('--unknown-types-strategy',
                                           dest='unknown_types_strategy',
                                           required=False,
                                           choices=['stop', 'ignore', 'add'],
                                           default='stop',
                                           help='strategy for unknown class types in annotation files\n'
                                           'stop: stop on unknown class type names\n'
                                           'ignore: ignore unknown class type names\n'
                                           'add: add unknown class types names to labels.yaml')
    import_dataset_arg_parser.add_argument('--anno-type',
                                           dest='anno_type',
                                           required=True,
                                           choices=['det-box', 'seg', 'no-annotations'],
                                           help='annotations type\n')
    import_dataset_arg_parser.add_argument('--ins-seg',
                                           dest='is_instance_segmentation',
                                           action='store_true',
                                           help='set if this dataset is instance segmentation')
    import_dataset_arg_parser.set_defaults(func=CmdImport)
