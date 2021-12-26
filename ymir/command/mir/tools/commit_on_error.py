import datetime
from functools import wraps
import traceback
from typing import Any, Callable

from mir.tools import mir_storage_ops, revs_parser
from mir.tools.code import MirCode, MirRuntimeError
from protos import mir_command_pb2 as mirpb


def _generate_mir_task(code: int, error_msg: str, dst_typ_rev_tid: revs_parser.TypRevTid) -> mirpb.MirTasks:
    mir_tasks = mirpb.MirTasks()  # TODO: READ OLD
    task = mirpb.Task()
    task.task_id = dst_typ_rev_tid.tid
    task.timestamp = int(datetime.datetime.now().timestamp())
    mir_storage_ops.add_mir_task(mir_tasks, task)
    return mir_tasks


def _commit_error(code: int, error_msg: str, mir_root: str, src_revs: str, dst_rev: str) -> None:
    src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
    dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)

    mir_metadatas = mirpb.MirMetadatas()
    mir_annotations = mirpb.MirAnnotations()
    mir_tasks = _generate_mir_task(code=code, error_msg=error_msg, dst_typ_rev_tid=dst_typ_rev_tid)
    mir_datas = {
        mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
        mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
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
                trace_message = f"cmd return: {ret}"
                _commit_error(code=ret, error_msg=trace_message, mir_root=mir_root, src_revs=src_revs, dst_rev=dst_rev)
        except MirRuntimeError as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"
            _commit_error(code=e.error_code,
                          error_msg=trace_message,
                          mir_root=mir_root,
                          src_revs=src_revs,
                          dst_rev=dst_rev)
            raise e
        except BaseException as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"
            _commit_error(code=MirCode.RC_RUNTIME_ERROR_UNKNOWN,
                          error_msg=trace_message,
                          mir_root=mir_root,
                          src_revs=src_revs,
                          dst_rev=dst_rev)
            raise e

    return wrapper
