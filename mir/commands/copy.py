import argparse
import datetime
import logging

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, revs_parser, mir_repo_utils, mir_storage, mir_storage_ops
from mir.tools.phase_logger import PhaseLoggerCenter, phase_logger_in_out
from mir.tools.code import MirCode


class CmdCopy(base.BaseCommand):
    # public: run cmd
    def run(self) -> int:
        logging.debug("command copy: %s", self.args)
        return CmdCopy.run_with_args(mir_root=self.args.mir_root,
                                     src_mir_root=self.args.src_mir_root,
                                     src_revs=self.args.src_revs,
                                     dst_rev=self.args.dst_rev,
                                     work_dir=self.args.work_dir)

    @staticmethod
    @phase_logger_in_out
    def run_with_args(mir_root: str, src_mir_root: str, src_revs: str, dst_rev: str, work_dir: str = None) -> int:
        # check args
        if not mir_root or not src_mir_root or not src_revs or not dst_rev:
            logging.error('invalid args: no mir_root, src_mir_root, src_revs or dst_rev')
            return MirCode.RC_CMD_INVALID_ARGS

        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
        if checker.check_src_revs(src_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS

        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)
        if checker.check_dst_rev(dst_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS

        PhaseLoggerCenter.create_phase_loggers(
            top_phase='copy',
            monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
            task_name=dst_typ_rev_tid.tid)

        check_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        check_code = checker.check(src_mir_root, prerequisites=[checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        # read from src mir root
        mir_datas = mir_storage_ops.MirStorageOps.load(mir_root=src_mir_root,
                                                       mir_branch=src_typ_rev_tid.rev,
                                                       mir_storages=mir_storage.get_all_mir_storage())

        PhaseLoggerCenter.update_phase(phase='copy.read')

        # annotations.mir: change head task id
        mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]
        orig_head_task_id = mir_annotations.head_task_id
        if not orig_head_task_id:
            logging.error('bad annotations.mir: empty head task id')
            return MirCode.RC_CMD_INVALID_MIR_FILE
        if ((len(mir_annotations.task_annotations) > 0 and orig_head_task_id not in mir_annotations.task_annotations)):
            logging.error(f"bad annotations.mir: can not find head task id: {orig_head_task_id}")
            return MirCode.RC_CMD_INVALID_MIR_FILE

        single_task_annotations = mir_annotations.task_annotations[orig_head_task_id]
        mir_annotations.task_annotations[dst_typ_rev_tid.tid].CopyFrom(single_task_annotations)
        del mir_annotations.task_annotations[orig_head_task_id]
        mir_annotations.head_task_id = dst_typ_rev_tid.tid

        # tasks.mir: get necessary head task infos, remove others and change head task id
        mir_tasks: mirpb.MirTasks = mir_datas[mirpb.MIR_TASKS]
        orig_head_task_id = mir_tasks.head_task_id
        if not orig_head_task_id:
            logging.error('bad tasks.mir: empty head task id')
            return MirCode.RC_CMD_INVALID_MIR_FILE
        if orig_head_task_id not in mir_tasks.tasks:
            logging.error(f"bad tasks.mir: can not find head task id: {orig_head_task_id}")
            return MirCode.RC_CMD_INVALID_MIR_FILE

        task = mirpb.Task()
        task.type = mirpb.TaskTypeCopyData
        task.name = f"copy from {src_mir_root}, src: {src_revs}, dst: {dst_rev}"
        task.task_id = dst_typ_rev_tid.tid
        task.timestamp = int(datetime.datetime.now().timestamp())
        if mir_tasks.tasks[orig_head_task_id].type == mirpb.TaskTypeTraining:
            task.model.CopyFrom(mir_tasks.tasks[orig_head_task_id].model)

        mir_tasks = mirpb.MirTasks()
        mir_tasks.head_task_id = dst_typ_rev_tid.tid
        mir_tasks.tasks[dst_typ_rev_tid.tid].CopyFrom(task)

        PhaseLoggerCenter.update_phase(phase='copy.change')

        mir_datas[mirpb.MIR_ANNOTATIONS] = mir_annotations
        mir_datas[mirpb.MIR_TASKS] = mir_tasks
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch='master',
                                                      mir_datas=mir_datas,
                                                      commit_message=task.name)

        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    copy_arg_parser = subparsers.add_parser("copy",
                                            parents=[parent_parser],
                                            description="use this command to copy datas from another repo",
                                            help="copy datas from another repo")
    copy_arg_parser.add_argument("--src-root",
                                 dest="src_mir_root",
                                 type=str,
                                 required=True,
                                 help="source mir root you want to copy from")
    copy_arg_parser.add_argument("--src-revs",
                                 dest="src_revs",
                                 type=str,
                                 required=True,
                                 help="type:rev@bid, branch in source mir root")
    copy_arg_parser.add_argument("--dst-rev", dest="dst_rev", type=str, required=True, help="rev@tid")
    copy_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    copy_arg_parser.set_defaults(func=CmdCopy)
