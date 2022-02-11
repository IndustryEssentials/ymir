import copy
import datetime
from functools import wraps
import logging
from subprocess import CalledProcessError
import traceback
from typing import Any, Callable

from mir.tools import mir_repo_utils, mir_storage_ops, phase_logger, revs_parser, utils
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


@utils.time_it
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

        exc: Any = None

        try:
            ret = f(mir_root=mir_root, src_revs=src_revs, dst_rev=dst_rev, work_dir=work_dir, *args, **kwargs)
        except MirRuntimeError as e:
            error_code = e.error_code
            state_message = e.error_message
            predefined_mir_tasks = e.mir_tasks
            needs_new_commit = e.needs_new_commit
            exc = copy.copy(e)
            trace_message = f"cmd exception: {traceback.format_exc()}"
        except CalledProcessError as e:
            error_code = MirCode.RC_CMD_CONTAINER_ERROR
            state_message = str(e)
            predefined_mir_tasks = None
            needs_new_commit = True
            exc = copy.copy(e)
            trace_message = f"cmd exception: {traceback.format_exc()}"
        except BaseException as e:
            error_code = MirCode.RC_CMD_ERROR_UNKNOWN
            state_message = str(e)
            predefined_mir_tasks = None
            needs_new_commit = True
            exc = copy.copy(e)
            trace_message = f"cmd exception: {traceback.format_exc()}"
        else:
            trace_message = f"cmd return: {ret}"

            if ret == MirCode.RC_OK:
                mir_logger.update_percent_info(local_percent=1, task_state=phase_logger.PhaseStateEnum.DONE)
            else:
                _commit_error(code=ret,
                              error_msg=trace_message,
                              mir_root=mir_root,
                              src_revs=src_revs,
                              dst_rev=dst_rev,
                              predefined_mir_tasks=None)
                mir_logger.update_percent_info(local_percent=1,
                                               task_state=phase_logger.PhaseStateEnum.ERROR,
                                               state_code=ret,
                                               state_content=trace_message,
                                               trace_message=trace_message)

            logging.info(f"command done: {dst_rev}, result: {ret}")
            return ret

        if needs_new_commit:
            _commit_error(code=error_code,
                          error_msg=trace_message,
                          mir_root=mir_root,
                          src_revs=src_revs,
                          dst_rev=dst_rev,
                          predefined_mir_tasks=predefined_mir_tasks)
        mir_logger.update_percent_info(local_percent=1,
                                       task_state=phase_logger.PhaseStateEnum.ERROR,
                                       state_code=error_code,
                                       state_content=state_message,
                                       trace_message=trace_message)
        logging.info(f"command fail: {dst_rev}, exc: {exc}, error_code: {error_code}, new commit: {needs_new_commit}")
        raise exc

    return wrapper
