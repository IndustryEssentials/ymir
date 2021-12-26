import datetime
from functools import wraps
import traceback
from typing import Any, Callable

from mir.tools import mir_storage, mir_storage_ops, revs_parser
from mir.tools.code import MirCode, MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


def _generate_mir_task(code: int, error_msg: str, dst_typ_rev_tid: revs_parser.TypRevTid) -> mirpb.Task:
    task = mirpb.Task()
    task.type = mirpb.TaskType.TaskTypeUnknown
    task.task_id = dst_typ_rev_tid.tid
    task.name = dst_typ_rev_tid.tid
    task.timestamp = int(datetime.datetime.now().timestamp())
    task.code = code
    task.error_msg = error_msg
    return task


def _commit_error(code: int, error_msg: str, mir_root: str, src_revs: str, dst_rev: str) -> None:
    src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
    dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)

    mir_tasks = mirpb.MirTasks()
    if src_revs != 'master':
        mir_tasks = mir_storage_ops.MirStorageOps.load_single(mir_root=mir_root,
                                                              mir_branch=src_typ_rev_tid.rev,
                                                              ms=mirpb.MIR_TASKS,
                                                              mir_task_id=src_typ_rev_tid.tid)

    task = _generate_mir_task(code=code, error_msg=error_msg, dst_typ_rev_tid=dst_typ_rev_tid)
    mir_storage_ops.add_mir_task(mir_tasks, task)
    mir_datas = {
        mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas(),
        mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations(),
        mirpb.MirStorage.MIR_TASKS: mir_tasks,
    }

    mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                  mir_branch=dst_typ_rev_tid.rev,
                                                  task_id=dst_typ_rev_tid.tid,
                                                  his_branch=src_typ_rev_tid.rev,
                                                  mir_datas=mir_datas,
                                                  commit_message='task failed')


def commit_on_error(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(mir_root: str, src_revs: str, dst_rev: str, *args: tuple, **kwargs: dict) -> Any:
        try:
            ret = f(mir_root=mir_root, src_revs=src_revs, dst_rev=dst_rev, *args, **kwargs)

            if ret != MirCode.RC_OK:
                if not mir_root:
                    mir_root = '.'
                if not src_revs:
                    src_revs = 'master'

                trace_message = f"cmd return: {ret}"
                _commit_error(code=ret, error_msg=trace_message, mir_root=mir_root, src_revs=src_revs, dst_rev=dst_rev)

            return ret
        except MirRuntimeError as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"
            _commit_error(code=e.error_code,
                          error_msg=trace_message,
                          mir_root=mir_root,
                          src_revs=src_revs,
                          dst_rev=dst_rev)
            raise e
        except Exception as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"
            _commit_error(code=MirCode.RC_RUNTIME_ERROR_UNKNOWN,
                          error_msg=trace_message,
                          mir_root=mir_root,
                          src_revs=src_revs,
                          dst_rev=dst_rev)
            raise e

    return wrapper
