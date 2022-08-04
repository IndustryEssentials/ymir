import argparse
import logging
import os
import random
import shutil

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import annotations, checker, hash_utils, metadatas, mir_repo_utils, mir_storage_ops, revs_parser, utils
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.phase_logger import PhaseLoggerCenter


class CmdImport(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command import: %s", self.args)

        return CmdImport.run_with_args(mir_root=self.args.mir_root,
                                       index_file=self.args.index_file,
                                       gt_index_file=self.args.gt_index_file,
                                       anno_abs=self.args.anno,
                                       gt_abs=self.args.gt_dir,
                                       gen_abs=self.args.gen,
                                       dataset_name=self.args.dataset_name,
                                       dst_rev=self.args.dst_rev,
                                       src_revs=self.args.src_revs or 'master',
                                       work_dir=self.args.work_dir,
                                       unknown_types_strategy=annotations.UnknownTypesStrategy(
                                           self.args.unknown_types_strategy))

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, index_file: str, gt_index_file: str, anno_abs: str, gt_abs: str, gen_abs: str,
                      dataset_name: str, dst_rev: str, src_revs: str, work_dir: str,
                      unknown_types_strategy: annotations.UnknownTypesStrategy) -> int:
        # Step 1: check args and prepare environment.
        if not index_file or not gen_abs or not os.path.isfile(index_file):
            logging.error(f"invalid index_file: {index_file} or gen_abs: {gen_abs}")
            return MirCode.RC_CMD_INVALID_ARGS
        if anno_abs and not os.path.isdir(anno_abs):
            logging.error(f"annotations dir invalid: {anno_abs}")
            return MirCode.RC_CMD_INVALID_ARGS
        if gt_abs:  # need to import ground-truth data.
            if not os.path.isdir(gt_abs):
                logging.error(f"groundtruth dir invalid: {gt_abs}")
                return MirCode.RC_CMD_INVALID_ARGS
            if not gt_index_file or not os.path.isfile(gt_index_file):
                logging.error(f"invalid gt_index_file: {gt_index_file}")
                return MirCode.RC_CMD_INVALID_ARGS
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)

        if not dataset_name:
            dataset_name = dst_typ_rev_tid.tid

        PhaseLoggerCenter.create_phase_loggers(top_phase='import',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name=dst_typ_rev_tid.tid)

        check_code = checker.check(mir_root,
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if check_code != MirCode.RC_OK:
            return check_code

        # Step 2: generate sha1 file and rename images.
        # sha1 file to be written.
        sha1_index_abs = os.path.join(
            gen_abs, f"{os.path.basename(index_file)}-{dst_typ_rev_tid.rev}-{random.randint(0, 100)}.sha1")
        ret = _generate_sha_and_copy(index_file, sha1_index_abs, gen_abs)
        if ret != MirCode.RC_OK:
            logging.error(f"generate hash error: {ret}")
            return ret

        sha1_gt_index_abs = ""
        if gt_index_file:
            if gt_index_file != index_file:  # a seperate gt_index_file is provided.
                sha1_gt_index_abs = os.path.join(
                    gen_abs, f"{os.path.basename(gt_index_file)}-{dst_typ_rev_tid.rev}-{random.randint(0, 100)}.sha1")
                ret = _generate_sha_and_copy(gt_index_file, sha1_gt_index_abs, gen_abs)
                if ret != MirCode.RC_OK:
                    logging.error(f"generate gt_index hash error: {ret}")
                    return ret
            else:
                sha1_gt_index_abs = sha1_index_abs

        # Step 3 import metadat and annotations:
        mir_metadatas = mirpb.MirMetadatas()
        ret = metadatas.import_metadatas(mir_metadatas=mir_metadatas,
                                         dataset_name=dataset_name,
                                         in_sha1_path=sha1_index_abs,
                                         hashed_asset_root=gen_abs,
                                         phase='import.metadatas')
        if ret != MirCode.RC_OK:
            logging.error(f"import metadatas error: {ret}")
            return ret

        mir_annotation = mirpb.MirAnnotations()
        anno_import_result = annotations.import_annotations(mir_metadatas=mir_metadatas,
                                                            mir_annotation=mir_annotation,
                                                            in_sha1_file=sha1_index_abs,
                                                            in_sha1_gt_file=sha1_gt_index_abs,
                                                            mir_root=mir_root,
                                                            annotations_dir_path=anno_abs,
                                                            groundtruth_dir_path=gt_abs,
                                                            unknown_types_strategy=unknown_types_strategy,
                                                            task_id=dst_typ_rev_tid.tid,
                                                            phase='import.others')

        logging.info(f"unknown types strategy: {unknown_types_strategy}")
        logging.info(f"anno import result: {anno_import_result}")

        # create and write tasks
        task = mir_storage_ops.create_task(
            task_type=mirpb.TaskTypeImportData,
            task_id=dst_typ_rev_tid.tid,
            message=f"importing {index_file}-{anno_abs}-{gt_abs} to {dst_rev}, uts: {unknown_types_strategy}",
            new_types={k: v.count
                       for k, v in anno_import_result.items()},
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

        # cleanup
        os.remove(sha1_index_abs)

        return MirCode.RC_OK


def _generate_sha_and_copy(index_file: str, sha_idx_file: str, sha_folder: str) -> int:
    hash_phase_name = 'import.hash'
    if not os.path.isfile(index_file):
        logging.error('invalid index_file')
        return MirCode.RC_CMD_INVALID_ARGS

    os.makedirs(sha_folder, exist_ok=True)

    with open(index_file) as idx_f, open(sha_idx_file, 'w') as sha_f:
        lines = idx_f.readlines()
        total_count = len(lines)
        asset_count_limit = 1000000
        if total_count > asset_count_limit:  # large number of images may trigger redis timeout error.
            logging.error(f'# of image {total_count} exceeds upper boundary {asset_count_limit}.')
            return MirCode.RC_CMD_INVALID_ARGS

        idx = 0
        for line in lines:
            media_src = line.strip()
            if not media_src or not os.path.isfile(media_src):
                logging.warning("invalid file: ", media_src)
                continue

            sha1 = hash_utils.sha1sum_for_file(media_src)
            sha_f.writelines("\t".join([sha1, media_src]) + '\n')

            media_dst = utils.get_asset_storage_path(location=sha_folder, hash=sha1, make_dirs=True)
            if not os.path.isfile(media_dst):
                shutil.copyfile(media_src, media_dst)

            idx += 1
            if idx % 5000 == 0:
                PhaseLoggerCenter.update_phase(phase=hash_phase_name, local_percent=(idx / total_count))
                logging.info(f"finished {idx} / {total_count} hashes")
    PhaseLoggerCenter.update_phase(phase=hash_phase_name)
    return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    importing_arg_parser = subparsers.add_parser("import",
                                                 parents=[parent_parser],
                                                 description="use this command to import data from img/anno folder",
                                                 help="import raw data",
                                                 formatter_class=argparse.RawTextHelpFormatter)
    importing_arg_parser.add_argument("--index-file",
                                      dest="index_file",
                                      type=str,
                                      help="index of input media, one file per line")
    importing_arg_parser.add_argument("--annotation-dir",
                                      dest="anno",
                                      type=str,
                                      required=False,
                                      help="corresponding annotation folder")
    importing_arg_parser.add_argument("--gt-index-file",
                                      dest="gt_index_file",
                                      type=str,
                                      help="index of input gt annotation, one file per line")
    importing_arg_parser.add_argument("--gt-dir",
                                      dest="gt_dir",
                                      type=str,
                                      required=False,
                                      help="corresponding ground-truth folder")
    importing_arg_parser.add_argument("--gen-dir", dest="gen", type=str, help="storage path of generated data files")
    importing_arg_parser.add_argument("--dataset-name",
                                      dest="dataset_name",
                                      type=str,
                                      required=False,
                                      help="name of the dataset to be created, use tid if not set.")
    importing_arg_parser.add_argument("--src-revs", dest="src_revs", type=str, help="rev: source rev")
    importing_arg_parser.add_argument("--dst-rev",
                                      dest="dst_rev",
                                      type=str,
                                      required=True,
                                      help="rev@tid: destination branch name and task id")
    importing_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    importing_arg_parser.add_argument('--unknown-types-strategy',
                                      dest='unknown_types_strategy',
                                      required=False,
                                      choices=['stop', 'ignore', 'add'],
                                      default='stop',
                                      help='strategy for unknown class types in annotation files\n'
                                      'stop: stop on unknown class type names\n'
                                      'ignore: ignore unknown class type names\n'
                                      'add: add unknown class types names to labels.yaml')
    importing_arg_parser.set_defaults(func=CmdImport)
