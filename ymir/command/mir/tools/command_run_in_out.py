import datetime
from functools import wraps
from subprocess import CalledProcessError
import traceback
from typing import Any, Callable

from mir.tools import mir_repo_utils, mir_storage_ops, revs_parser, phase_logger
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


# private: monitor.txt logger
def _get_task_name(dst_rev: str) -> str:
    return revs_parser.parse_single_arg_rev(dst_rev).tid if dst_rev else 'default_task'


# private: commit on errors
def _generate_mir_task(code: int, error_msg: str, dst_typ_rev_tid: revs_parser.TypRevTid) -> mirpb.Task:
    task = mirpb.Task()
    task.type = mirpb.TaskType.TaskTypeUnknown
    task.task_id = dst_typ_rev_tid.tid
    task.name = dst_typ_rev_tid.tid
    task.timestamp = int(datetime.datetime.now().timestamp())
    task.return_code = code
    task.return_msg = error_msg
    return task


def _commit_error(code: int, error_msg: str, mir_root: str, src_revs: str, dst_rev: str,
                  predefined_mir_tasks: Any) -> None:
    if not src_revs:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty src_revs',
                              needs_new_commit=False)
    if not dst_rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty dst_rev',
                              needs_new_commit=False)

    src_typ_rev_tid = revs_parser.parse_arg_revs(src_revs)[0]
    dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)
    if predefined_mir_tasks:
        mir_tasks = predefined_mir_tasks
    else:
        mir_tasks = mirpb.MirTasks()
        if src_revs != 'master':
            mir_tasks = mir_storage_ops.MirStorageOps.load_single(mir_root=mir_root,
                                                                  mir_branch=src_typ_rev_tid.rev,
                                                                  ms=mirpb.MIR_TASKS,
                                                                  mir_task_id=src_typ_rev_tid.tid)
        task = _generate_mir_task(code=code, error_msg=error_msg, dst_typ_rev_tid=dst_typ_rev_tid)
        mir_storage_ops.add_mir_task(mir_tasks, task)

    mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                  mir_branch=dst_typ_rev_tid.rev,
                                                  task_id=dst_typ_rev_tid.tid,
                                                  his_branch=src_typ_rev_tid.rev,
                                                  mir_datas={mirpb.MirStorage.MIR_TASKS: mir_tasks},
                                                  commit_message='task failed')


def command_run_in_out(f: Callable) -> Callable:
    """
    record monitor.txt and commit on errors
    """
    @wraps(f)
    def wrapper(mir_root: str, src_revs: str, dst_rev: str, work_dir: str, *args: tuple, **kwargs: dict) -> Any:
        mir_logger = phase_logger.PhaseLogger(task_name=_get_task_name(dst_rev),
                                              monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir))
        mir_logger.update_percent_info(local_percent=0, task_state=phase_logger.PhaseStateEnum.PENDING)

        try:
            ret = f(mir_root=mir_root, src_revs=src_revs, dst_rev=dst_rev, work_dir=work_dir, *args, **kwargs)
            trace_message = f"cmd return: {ret}"

            if ret == MirCode.RC_OK:
                mir_logger.update_percent_info(local_percent=1, task_state=phase_logger.PhaseStateEnum.DONE)
            else:
                mir_logger.update_percent_info(local_percent=1,
                                               task_state=phase_logger.PhaseStateEnum.ERROR,
                                               state_code=ret,
                                               state_content=trace_message,
                                               trace_message=trace_message)
                _commit_error(code=ret,
                              error_msg=trace_message,
                              mir_root=mir_root,
                              src_revs=src_revs,
                              dst_rev=dst_rev,
                              predefined_mir_tasks=None)

            return ret
        except MirRuntimeError as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"

            mir_logger.update_percent_info(local_percent=1,
                                           task_state=phase_logger.PhaseStateEnum.ERROR,
                                           state_code=e.error_code,
                                           state_content=e.error_message,
                                           trace_message=trace_message)
            if e.needs_new_commit:
                _commit_error(code=e.error_code,
                              error_msg=trace_message,
                              mir_root=mir_root,
                              src_revs=src_revs,
                              dst_rev=dst_rev,
                              predefined_mir_tasks=e.mir_tasks)

            raise e
        except CalledProcessError as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"

            mir_logger.update_percent_info(local_percent=1,
                                           task_state=phase_logger.PhaseStateEnum.ERROR,
                                           state_code=MirCode.RC_RUNTIME_CONTAINER_ERROR,
                                           state_content=str(e),
                                           trace_message=trace_message)

            raise e
        except BaseException as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"
            mir_logger.update_percent_info(local_percent=1,
                                           task_state=phase_logger.PhaseStateEnum.ERROR,
                                           state_code=MirCode.RC_RUNTIME_ERROR_UNKNOWN,
                                           state_content=str(e),
                                           trace_message=trace_message)
            raise e

    return wrapper
