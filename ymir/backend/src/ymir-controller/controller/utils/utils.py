import logging
import re
import subprocess

from id_definition import task_id as task_id_proto
from controller.utils.code import ResCode
from proto import backend_pb2


def mir_executable() -> str:
    """get mir executable command in container"""
    return "mir"


def run_command(cmd: str) -> backend_pb2.GeneralResp:
    logging.info(f"starting cmd: \n{cmd}\n")
    result = subprocess.run(cmd, capture_output=True, shell=True, text=True)  # run and wait
    if result.returncode != 0:
        logging.error(f"run cmd error:\n {result.stderr}")
        return make_general_response(ResCode.CTR_ERROR_UNKNOWN, result.stderr)

    logging.info(f"run cmd succeed: \n {result.stdout}")
    return make_general_response(ResCode.CTR_OK, result.stdout)


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
    format_enum_dict = {backend_pb2.NO_ANNOTATION: 'none', backend_pb2.PASCAL_VOC: 'voc', backend_pb2.IF_ARK: 'ark'}
    return format_enum_dict[format]
