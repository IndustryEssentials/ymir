import argparse
import logging
from typing import Dict, List

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, revs_parser, mir_repo_utils, mir_storage_ops
from mir.tools.annotations import map_and_filter_annotations
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter


class CmdCopy(base.BaseCommand):
    # public: run cmd
    def run(self) -> int:
        logging.debug("command copy: %s", self.args)
        return CmdCopy.run_with_args(mir_root=self.args.mir_root,
                                     label_storage_file=self.args.label_storage_file,
                                     data_mir_root=self.args.data_mir_root,
                                     data_src_revs=self.args.data_src_revs,
                                     data_label_storage_file=self.args.data_label_storage_file,
                                     dst_rev=self.args.dst_rev,
                                     ignore_unknown_types=self.args.ignore_unknown_types,
                                     drop_annotations=self.args.drop_annotations,
                                     src_revs='master',
                                     work_dir=self.args.work_dir)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str,
                      label_storage_file: str,
                      data_mir_root: str,
                      data_src_revs: str,
                      data_label_storage_file: str,
                      dst_rev: str,
                      ignore_unknown_types: bool,
                      drop_annotations: bool,
                      src_revs: str = 'master',
                      work_dir: str = None) -> int:
        # ! pay attention to param: `src_revs` and `data_src_revs`
        # ! data_src_revs means the source branch in data_mir_root
        # ! src_revs means the source branch we commit from, in this destination mir_root
        # ! and src_revs also needed by decorator @command_run_in_out
        # check args
        if not mir_root or not data_mir_root or not data_src_revs or not dst_rev:
            logging.error('invalid args: no mir_root, data_mir_root, data_src_revs or dst_rev')
            return MirCode.RC_CMD_INVALID_ARGS

        data_src_typ_rev_tid = revs_parser.parse_single_arg_rev(data_src_revs, need_tid=False)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        PhaseLoggerCenter.create_phase_loggers(top_phase='copy',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name=dst_typ_rev_tid.tid)

        check_code = checker.check(mir_root,
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        check_code = checker.check(
            data_mir_root, prerequisites=[checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        PhaseLoggerCenter.update_phase(phase="copy.init")

        # read from src mir root
        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_tasks: mirpb.MirTasks
        mir_metadatas, mir_annotations, mir_tasks = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=data_mir_root,
            mir_branch=data_src_typ_rev_tid.rev,
            mir_task_id=data_src_typ_rev_tid.tid,
            ms_list=[mirpb.MIR_METADATAS, mirpb.MIR_ANNOTATIONS, mirpb.MIR_TASKS],
            as_dict=False)

        PhaseLoggerCenter.update_phase(phase='copy.read')

        unknown_class_names: List[str] = []
        if drop_annotations:
            mir_annotations.prediction.Clear()
            mir_annotations.prediction.type = mirpb.ObjectType.OT_NO_ANNOTATIONS
            mir_annotations.prediction.is_instance_segmentation = False
            mir_annotations.ground_truth.Clear()
            mir_annotations.ground_truth.type = mirpb.ObjectType.OT_NO_ANNOTATIONS
            mir_annotations.ground_truth.is_instance_segmentation = False
        else:
            unknown_class_names = map_and_filter_annotations(mir_annotations=mir_annotations,
                                                             data_label_storage_file=data_label_storage_file,
                                                             label_storage_file=label_storage_file)

        if unknown_class_names:
            if ignore_unknown_types:
                logging.warning(f"unknown types: {unknown_class_names}")
            else:
                raise MirRuntimeError(
                    error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                    error_message=f"copy annotations error, unknown class names: {unknown_class_names}")

        PhaseLoggerCenter.update_phase(phase='copy.change')

        # save and commit
        orig_task: mirpb.Task = mir_tasks.tasks[mir_tasks.head_task_id]
        task = mir_storage_ops.create_task_record(
            task_type=mirpb.TaskType.TaskTypeCopyData,
            task_id=dst_typ_rev_tid.tid,
            message=f"copy from {data_mir_root}, src: {data_src_revs}, dst: {dst_rev}",
            new_types={name: 0
                       for name in unknown_class_names},
            model_meta=orig_task.model,
            serialized_executor_config=orig_task.serialized_executor_config,
            executor=orig_task.executor,
            src_revs=src_revs,
            dst_rev=dst_rev)
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=src_revs,
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

        return MirCode.RC_OK

    @staticmethod
    def _change_type_ids(
        single_task_annotations: mirpb.SingleTaskAnnotations,
        src_to_dst_ids: Dict[int, int],
    ) -> None:
        for single_image_annotations in single_task_annotations.image_annotations.values():
            dst_image_annotations: List[mirpb.ObjectAnnotation] = []
            for annotation in single_image_annotations.boxes:
                dst_class_id = src_to_dst_ids[annotation.class_id]
                if dst_class_id >= 0:
                    annotation.class_id = dst_class_id
                    dst_image_annotations.append(annotation)
            del single_image_annotations.boxes[:]
            single_image_annotations.boxes.extend(dst_image_annotations)

        dst_eval_class_ids: List[int] = []
        for src_class_id in single_task_annotations.eval_class_ids:
            dst_class_id = src_to_dst_ids[src_class_id]
            if dst_class_id >= 0:
                dst_eval_class_ids.append(dst_class_id)
        single_task_annotations.eval_class_ids[:] = dst_eval_class_ids

    @staticmethod
    def _gen_unknown_names_and_count(src_class_id_mgr: class_ids.UserLabels, mir_context: mirpb.MirContext,
                                     src_to_dst_ids: Dict[int, int]) -> Dict[str, int]:
        all_src_class_ids = set(mir_context.pred_stats.class_ids_cnt.keys()) | set(
            mir_context.gt_stats.class_ids_cnt.keys())
        unknown_src_class_ids = {src_id for src_id in all_src_class_ids if src_to_dst_ids[src_id] == -1}
        if not unknown_src_class_ids:
            return {}

        unknown_names_and_count: Dict[str, int] = {}
        for src_id in unknown_src_class_ids:
            name = src_class_id_mgr.main_name_for_id(src_id)
            cnt_gt: int = mir_context.pred_stats.class_ids_cnt[src_id]
            cnt_pred: int = mir_context.gt_stats.class_ids_cnt[src_id]
            unknown_names_and_count[name] = cnt_gt + cnt_pred
        return unknown_names_and_count


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    copy_arg_parser = subparsers.add_parser("copy",
                                            parents=[parent_parser],
                                            description="use this command to copy datas from another repo",
                                            help="copy datas from another repo")
    copy_arg_parser.add_argument("--src-root",
                                 dest="data_mir_root",
                                 type=str,
                                 required=True,
                                 help="source mir root you want to copy from")
    copy_arg_parser.add_argument("--src-revs",
                                 dest="data_src_revs",
                                 type=str,
                                 required=True,
                                 help="type:rev@bid, branch in source mir root")
    copy_arg_parser.add_argument("--src-user-label-file",
                                 dest="data_label_storage_file",
                                 type=str,
                                 required=False,
                                 help="source label storage file path you want to copy from")
    copy_arg_parser.add_argument("--dst-rev", dest="dst_rev", type=str, required=True, help="rev@tid")
    copy_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    copy_arg_parser.add_argument('--ignore-unknown-types',
                                 dest='ignore_unknown_types',
                                 required=False,
                                 action='store_true',
                                 help='ignore unknown type names in annotation files')
    copy_arg_parser.add_argument('--drop-annotations',
                                 dest='drop_annotations',
                                 required=False,
                                 action='store_true',
                                 help='drop all annotations when copy')
    copy_arg_parser.set_defaults(func=CmdCopy)
