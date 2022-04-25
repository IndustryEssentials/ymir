import argparse
from collections import defaultdict
import logging
from typing import Dict, List, Set, Tuple

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, revs_parser, mir_repo_utils, mir_storage, mir_storage_ops
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.tools.code import MirCode


class CmdCopy(base.BaseCommand):
    # public: run cmd
    def run(self) -> int:
        logging.debug("command copy: %s", self.args)
        return CmdCopy.run_with_args(mir_root=self.args.mir_root,
                                     data_mir_root=self.args.data_mir_root,
                                     data_src_revs=self.args.data_src_revs,
                                     dst_rev=self.args.dst_rev,
                                     ignore_unknown_types=self.args.ignore_unknown_types,
                                     drop_annotations=self.args.drop_annotations,
                                     src_revs='master',
                                     work_dir=self.args.work_dir)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str,
                      data_mir_root: str,
                      data_src_revs: str,
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
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if check_code != MirCode.RC_OK:
            return check_code

        check_code = checker.check(
            data_mir_root, prerequisites=[checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if check_code != MirCode.RC_OK:
            return check_code

        # read from src mir root
        [mir_metadatas, mir_annotations, mir_keywords, mir_tasks,
         _] = mir_storage_ops.MirStorageOps.load_multiple_storages(mir_root=data_mir_root,
                                                                   mir_branch=data_src_typ_rev_tid.rev,
                                                                   mir_task_id=data_src_typ_rev_tid.tid,
                                                                   ms_list=mir_storage.get_all_mir_storage(),
                                                                   as_dict=False)

        PhaseLoggerCenter.update_phase(phase='copy.read')

        orig_head_task_id = mir_annotations.head_task_id
        if not orig_head_task_id:
            logging.error('bad annotations.mir: empty head task id')
            return MirCode.RC_CMD_INVALID_MIR_REPO
        if ((len(mir_annotations.task_annotations) > 0
                and orig_head_task_id not in mir_annotations.task_annotations)):
            logging.error(f"bad annotations.mir: can not find head task id: {orig_head_task_id}")
            return MirCode.RC_CMD_INVALID_MIR_REPO

        unknown_types: Dict[str, int] = {}
        if not drop_annotations:
            # if don't want to drop annotations
            # annotations.mir and keywords.mir: change type ids
            single_task_annotations = mir_annotations.task_annotations[orig_head_task_id]
            return_code, unknown_types = CmdCopy._change_type_ids(single_task_annotations=single_task_annotations,
                                                                  mir_keywords=mir_keywords,
                                                                  data_mir_root=data_mir_root,
                                                                  dst_mir_root=mir_root)
            if return_code != MirCode.RC_OK:
                logging.error(f"change annotation type ids failed: {return_code}")
                return return_code
            if unknown_types:
                if ignore_unknown_types:
                    logging.warning(f"unknown types: {unknown_types}")
                else:
                    logging.error(f"copy annotations error, unknown types: {unknown_types}")
                    return MirCode.RC_CMD_INVALID_MIR_REPO

            # annotations.mir: change head task id
            mir_annotations.task_annotations[dst_typ_rev_tid.tid].CopyFrom(single_task_annotations)
            del mir_annotations.task_annotations[orig_head_task_id]
            mir_annotations.head_task_id = dst_typ_rev_tid.tid

            # tasks.mir: get necessary head task infos, remove others and change head task id
            orig_head_task_id = mir_tasks.head_task_id
            if not orig_head_task_id:
                logging.error('bad tasks.mir: empty head task id')
                return MirCode.RC_CMD_INVALID_MIR_REPO
            if orig_head_task_id not in mir_tasks.tasks:
                logging.error(f"bad tasks.mir: can not find head task id: {orig_head_task_id}")
                return MirCode.RC_CMD_INVALID_MIR_REPO
        else:
            # if drop annotations, create an empty new mir_annotations
            mir_annotations = mirpb.MirAnnotations()
            mir_annotations.task_annotations[dst_typ_rev_tid.tid].CopyFrom(mirpb.SingleTaskAnnotations())
            mir_annotations.head_task_id = dst_typ_rev_tid.tid

        PhaseLoggerCenter.update_phase(phase='copy.change')

        # save and commit
        orig_task = mir_tasks.tasks[orig_head_task_id]
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeCopyData,
                                           task_id=dst_typ_rev_tid.tid,
                                           message=f"copy from {data_mir_root}, src: {data_src_revs}, dst: {dst_rev}",
                                           unknown_types=unknown_types,
                                           model_hash=orig_task.model.model_hash,
                                           model_mAP=orig_task.model.mean_average_precision,
                                           serialized_task_parameters=orig_task.serialized_task_parameters,
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
        mir_keywords: mirpb.MirKeywords,
        data_mir_root: str,
        dst_mir_root: str,
    ) -> Tuple[int, Dict[str, int]]:
        src_to_dst_ids: Dict[int, int] = {}
        unknown_types_and_count: Dict[str, int] = defaultdict(int)
        dst_class_id_mgr = class_ids.ClassIdManager(mir_root=dst_mir_root)
        src_class_id_mgr = class_ids.ClassIdManager(mir_root=data_mir_root)

        for asset_id, single_image_annotations in single_task_annotations.image_annotations.items():
            dst_keyids_set: Set[int] = set()
            dst_image_annotations: List[mirpb.Annotation] = []
            for annotation in single_image_annotations.annotations:
                src_type_id = annotation.class_id
                if not src_class_id_mgr.has_id(src_type_id):
                    # if we can not find src type id in data_mir_root's labels.csv, this repo in invalid and cannot copy
                    logging.error(f"broken data_mir_root, unknown src id: {annotation.class_id}")
                    return MirCode.RC_CMD_INVALID_MIR_REPO, unknown_types_and_count

                if src_type_id in src_to_dst_ids:
                    # get mapping from cache
                    annotation.class_id = src_to_dst_ids[src_type_id]
                    dst_image_annotations.append(annotation)
                else:
                    # if no cache, src_id -> src_type_name -> dst_id
                    src_type_name = src_class_id_mgr.main_name_for_id(src_type_id) or ''
                    if dst_class_id_mgr.has_name(src_type_name):
                        annotation.class_id = dst_class_id_mgr.id_and_main_name_for_name(src_type_name)[0]
                        dst_image_annotations.append(annotation)

                        src_to_dst_ids[src_type_id] = annotation.class_id  # save cache
                        dst_keyids_set.add(annotation.class_id)
                    else:
                        unknown_types_and_count[src_type_name] += 1

            del single_image_annotations.annotations[:]
            single_image_annotations.annotations.extend(dst_image_annotations)
            mir_keywords.keywords[asset_id].predifined_keyids[:] = dst_keyids_set
        return MirCode.RC_OK, unknown_types_and_count


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
