import logging
import re
import subprocess
import time
from functools import wraps
from typing import Callable, Dict, List

from controller.config import label_task as label_task_config
from controller.label_model.base import LabelBase
from controller.label_model.label_free import LabelFree
from controller.label_model.label_studio import LabelStudio
from id_definition import task_id as task_id_proto
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


def mir_executable() -> str:
    """get mir executable command in container"""
    return "mir"


def run_command(cmd: List[str],
                error_code: int = CTLResponseCode.RUN_COMMAND_ERROR) -> backend_pb2.GeneralResp:
    logging.info(f"starting cmd: \n{' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True)  # run and wait
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


def annotation_format_str(format: backend_pb2.LabelFormat) -> str:
    format_enum_dict = {
        backend_pb2.LabelFormat.NO_ANNOTATION: 'none',
        backend_pb2.LabelFormat.PASCAL_VOC: 'voc',
        backend_pb2.LabelFormat.IF_ARK: 'ark',
        backend_pb2.LabelFormat.LABEL_STUDIO_JSON: 'ls_json',
    }
    return format_enum_dict[format]


def time_it(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: Dict) -> Callable:
        _start = time.time()
        _ret = f(*args, **kwargs)
        _cost = time.time() - _start
        logging.info(f"|-{f.__name__} costs {_cost:.2f}s({_cost / 60:.2f}m).")
        return _ret

    return wrapper


def create_label_instance() -> LabelBase:
    if label_task_config.LABEL_TOOL == label_task_config.LABEL_STUDIO:
        label_instance = LabelStudio()
    elif label_task_config.LABEL_TOOL == label_task_config.LABEL_FREE:
        label_instance = LabelFree()  # type: ignore
    else:
        raise ValueError("Error! Please setting your label tools")

    return label_instance
