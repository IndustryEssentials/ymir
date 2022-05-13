import copy
from functools import wraps
import logging
import os
import shutil
import traceback
from typing import Any, Callable, Set

from mir.tools import mir_repo_utils, mir_storage_ops, phase_logger, revs_parser, utils
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


# private: monitor.txt logger
def _get_task_name(dst_rev: str) -> str:
    return revs_parser.parse_single_arg_rev(dst_rev, need_tid=True).tid if dst_rev else 'default_task'


@utils.time_it
def _commit_error(code: int, error_msg: str, mir_root: str, src_revs: str, dst_rev: str, predefined_task: Any) -> None:
    if not src_revs:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty src_revs',
                              needs_new_commit=False)
    if not dst_rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty dst_rev',
                              needs_new_commit=False)

    src_typ_rev_tid = revs_parser.parse_arg_revs(src_revs)[0]
    dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)
    if not predefined_task:
        predefined_task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeUnknown,
                                                      task_id=dst_typ_rev_tid.tid,
                                                      message='task failed',
                                                      return_code=code,
                                                      return_msg=error_msg,
                                                      src_revs=src_revs,
                                                      dst_rev=dst_rev)

    mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                  mir_branch=dst_typ_rev_tid.rev,
                                                  his_branch=src_typ_rev_tid.rev,
                                                  mir_datas={},
                                                  task=predefined_task)


def _cleanup_dir_sub_items(dir: str, ignored_items: Set[str]) -> None:
    if not os.path.isdir(dir):
        return

    dir_items = os.listdir(dir)
    for item in dir_items:
        if item in ignored_items:
            continue

        item_path = os.path.join(dir, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        elif os.path.isfile(item_path):
            os.remove(item_path)


def _cleanup(work_dir: str) -> None:
    if not work_dir:
        return

    _cleanup_dir_sub_items(work_dir, ignored_items={'out'})

    _cleanup_dir_sub_items(
        os.path.join(work_dir, 'out'),
        ignored_items={
            'log.txt',  # see also: ymir-cmd-container.md
            'monitor.txt',  # monitor file
            'monitor-log.txt',  # monitor detail file
            'tensorboard',  # default root directory for tensorboard event files
            'ymir-executor-out.log',  # container output
        })


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
            predefined_task = e.task
            needs_new_commit = e.needs_new_commit
            exc = copy.copy(e)
            trace_message = predefined_task.return_msg if (
                predefined_task and predefined_task.return_msg) else f"cmd exception: {traceback.format_exc()}"
        except BaseException as e:
            error_code = MirCode.RC_CMD_ERROR_UNKNOWN
            state_message = str(e)
            predefined_task = None
            needs_new_commit = True
            exc = copy.copy(e)
            trace_message = f"cmd exception: {traceback.format_exc()}"
        else:
            # if no exception
            state_message = f"cmd return: {ret}"

            if ret == MirCode.RC_OK:
                mir_logger.update_percent_info(local_percent=1, task_state=phase_logger.PhaseStateEnum.DONE)
                # no need to call _commit_error, already committed inside command run function
            else:
                _commit_error(code=ret,
                              error_msg=state_message,
                              mir_root=mir_root,
                              src_revs=src_revs,
                              dst_rev=dst_rev,
                              predefined_task=None)
                mir_logger.update_percent_info(local_percent=1,
                                               task_state=phase_logger.PhaseStateEnum.ERROR,
                                               state_code=ret,
                                               state_content=state_message,
                                               trace_message='')

            logging.info(f"command done: {dst_rev}, return code: {ret}")

            _cleanup(work_dir=work_dir)

            return ret

        # if MirContainerError, MirRuntimeError and BaseException occured
        # exception saved in exc
        if needs_new_commit:
            _commit_error(code=error_code,
                          error_msg=trace_message,
                          mir_root=mir_root,
                          src_revs=src_revs,
                          dst_rev=dst_rev,
                          predefined_task=predefined_task)
        mir_logger.update_percent_info(local_percent=1,
                                       task_state=phase_logger.PhaseStateEnum.ERROR,
                                       state_code=error_code,
                                       state_content=state_message,
                                       trace_message=trace_message)

        logging.info(f"command failed: {dst_rev}; exc: {exc}")
        logging.info(f"trace: {trace_message}")

        _cleanup(work_dir=work_dir)

        raise exc

    return wrapper
