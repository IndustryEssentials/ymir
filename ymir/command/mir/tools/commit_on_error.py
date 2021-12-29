import datetime
from functools import wraps
import traceback
from typing import Any, Callable

from mir.tools import mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


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
        src_revs = 'master'
    if not dst_rev:
        # not enough infos for us to generate a commit, because in ymir-command, dst-rev is always provided
        return

    src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
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

    mir_annotations = mirpb.MirAnnotations()
    mir_annotations.task_annotations[dst_typ_rev_tid.tid]  # an empty task annotations for hid
    mir_datas = {
        mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas(),
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
                _commit_error(code=ret,
                              error_msg=trace_message,
                              mir_root=mir_root,
                              src_revs=src_revs,
                              dst_rev=dst_rev,
                              predefined_mir_tasks=None)

            return ret
        except MirRuntimeError as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"
            if e.needs_new_commit:
                _commit_error(code=e.error_code,
                              error_msg=trace_message,
                              mir_root=mir_root,
                              src_revs=src_revs,
                              dst_rev=dst_rev,
                              predefined_mir_tasks=e.mir_tasks)
            raise e
        # other kind of errors: no commit, default behaviour

    return wrapper
