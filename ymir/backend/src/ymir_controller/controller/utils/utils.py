from functools import wraps
import logging
from pathlib import Path
import re
import subprocess
import time
from typing import Callable, Dict, List, Optional

from controller.config import label_task as label_task_config
from controller.label_model.base import LabelBase
from controller.label_model.label_free import LabelFree
from controller.utils.errors import MirCtrError
from id_definition import task_id as task_id_proto
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2


def mir_executable() -> str:
    """get mir executable command in container"""
    return "mir"


def index_repo(user_id: str, repo_id: str, task_id: str) -> backend_pb2.GeneralResp:
    index_command = ['./hel_server', 'viewer_client']
    index_command.extend(
        ['--user_id', user_id, '--repo_id', repo_id, '--task_id', task_id, 'index'])
    return run_command(index_command, cwd='/app/ymir_hel')


def run_command(cmd: List[str],
                error_code: int = CTLResponseCode.RUN_COMMAND_ERROR,
                cwd: str = None) -> backend_pb2.GeneralResp:
    logging.info(f"starting cmd: \n{' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)  # run and wait
    if result.returncode != 0:
        logging.error(f"run cmd error:\n stderr: {result.stderr} \n stdout: {result.stdout}")
        return make_general_response(error_code, result.stderr)

    logging.info(f"run cmd succeed: \n {result.stdout}")
    return make_general_response(CTLResponseCode.CTR_OK, result.stdout)


def check_valid_input_string(inputs: str,
                             backslash_ok: bool = False,
                             slash_ok: bool = False,
                             space_ok: bool = False) -> bool:
    max_string_length = 255
    if not inputs or len(inputs) > max_string_length:
        return False
    match_pattern = r'A-Za-z0-9\-_'
    if backslash_ok:
        match_pattern += '\\'
    if slash_ok:
        match_pattern += '/'
    if space_ok:
        match_pattern += ' '
    if not re.match("^[{}]+".format(match_pattern), inputs):
        return False
    return True


def make_general_response(code: int, message: str) -> backend_pb2.GeneralResp:
    response = backend_pb2.GeneralResp()
    response.code = code
    response.message = message
    return response


# In current task format, 2nd bit indicates the index of sub_task_id.
def sub_task_id(task_id: str, offset: int) -> str:
    if not task_id or len(task_id) != task_id_proto.IDProto.ID_LENGTH:
        raise RuntimeError("Invalid task id for sub_task: {}".format(task_id))
    if offset < 0 or offset > 9:
        raise RuntimeError("Invalid sub_task offset: {}".format(offset))
    return task_id[0] + str(offset) + task_id[2:]


def annotation_format_str(format: mir_cmd_pb.ExportFormat) -> str:
    format_enum_dict = {
        mir_cmd_pb.ExportFormat.EF_NO_ANNOTATIONS: 'none',
        mir_cmd_pb.ExportFormat.EF_VOC_XML: 'det-voc',
        mir_cmd_pb.ExportFormat.EF_ARK_TXT: 'det-ark',
        mir_cmd_pb.ExportFormat.EF_LS_JSON: 'det-ls-json',
        mir_cmd_pb.ExportFormat.EF_COCO_JSON: 'seg-coco',
    }
    return format_enum_dict[format]


def object_type_str(object_type: mir_cmd_pb.ObjectType) -> str:
    format_enum_dict = {
        mir_cmd_pb.ObjectType.OT_DET: 'det',
        mir_cmd_pb.ObjectType.OT_SEM_SEG: 'sem-seg',
        mir_cmd_pb.ObjectType.OT_INS_SEG: 'ins-seg',
        mir_cmd_pb.ObjectType.OT_MULTI_MODAL: 'multi-modal',
        mir_cmd_pb.ObjectType.OT_NO_ANNOS: 'no-annos',
    }
    return format_enum_dict[object_type]


def annotation_type_str(annotation_type: mir_cmd_pb.AnnotationType) -> str:
    enum_str_map = {
        mir_cmd_pb.AnnotationType.AT_GT: 'gt',
        mir_cmd_pb.AnnotationType.AT_PRED: 'pred',
    }
    return enum_str_map.get(annotation_type, 'any')


def time_it(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: Dict) -> Callable:
        _start = time.time()
        _ret = f(*args, **kwargs)
        _cost = time.time() - _start
        logging.info(f"|-{f.__name__} costs {_cost:.2f}s({_cost / 60:.2f}m).")
        return _ret

    return wrapper


def create_label_instance(user_token: Optional[str] = None) -> LabelBase:
    if label_task_config.LABEL_TOOL:
        label_instance = LabelFree(user_token)  # type: ignore
    else:
        raise ValueError("Error! Please enable LabelFree")

    return label_instance


def ensure_dirs_exist(paths: List[str]) -> None:
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def check_general_req_user_and_repo(req: backend_pb2.GeneralReq) -> None:
    all_tids = [req.task_id]  # tids from current req user
    if req.dst_dataset_id:
        all_tids.append(req.dst_dataset_id)
    all_tids.extend(req.ex_dataset_ids)
    if req.req_type == backend_pb2.RequestType.TASK_CREATE:
        if req.req_create_task.exporting.dataset_id:
            all_tids.append(req.req_create_task.exporting.dataset_id)
        all_tids.extend([x.dataset_id for x in req.req_create_task.training.in_dataset_types])

        is_copy_task = req.req_create_task.task_type == mir_cmd_pb.TaskTypeCopyData
        for tid in req.in_dataset_ids:
            # for copy task, only allowed to copy from "0001" (the admin / public dataset owner) or uid's repos
            # so skip those tids belongs to 0001
            if is_copy_task and "0001" == task_id_proto.TaskId.from_task_id(tid).user_id:
                continue
            all_tids.append(tid)
    else:
        all_tids.extend(req.in_dataset_ids)

    check_repo = req.req_create_task.task_type not in {mir_cmd_pb.TaskTypeCopyData, mir_cmd_pb.TaskTypeCopyModel}
    for tid in all_tids:
        task_id = task_id_proto.TaskId.from_task_id(tid)
        if req.user_id != task_id.user_id:
            raise MirCtrError(error_code=CTLResponseCode.INVOKER_INVALID_ARGS,
                              error_message=f"Task id mismatch: {tid} vs user: {req.user_id}")
        if check_repo and req.repo_id != task_id.repo_id:
            raise MirCtrError(error_code=CTLResponseCode.INVOKER_INVALID_ARGS,
                              error_message=f"Task id mismatch: {tid} vs repo: {req.repo_id}")
