import logging
import os
import sys
from enum import auto, IntEnum, unique
from typing import List

from controller.utils import utils
from id_definition import task_id as task_id_proto
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


@unique
class Prerequisites(IntEnum):
    UNUSED = 0
    CHECK_TASK_ID = auto()
    CHECK_USER_ID = auto()
    CHECK_USER_ROOT_EXIST = auto()
    CHECK_USER_ROOT_NOT_EXIST = auto()
    CHECK_REPO_ID = auto()
    CHECK_REPO_ROOT_EXIST = auto()
    CHECK_REPO_ROOT_NOT_EXIST = auto()
    CHECK_SINGLETON_OP = auto()
    CHECK_DST_DATASET_ID = auto()
    CHECK_GUEST_BRANCHES = auto()
    CHECK_COMMIT_MESSAGE = auto()
    CHECK_TASKINFO_IDS = auto()
    CHECK_SINGLE_IN_DATASET_ID = auto()
    CHECK_IN_DATASET_IDS = auto()
    CHECK_HIS_TASK_ID = auto()


# check controller request
def check_request(request: backend_pb2.GeneralReq,
                  prerequisites: List[Prerequisites] = [],
                  mir_root: str = None) -> backend_pb2.GeneralResp:
    for item in prerequisites:
        checker_name = "_{}".format(item.name.lower())
        checker_func = getattr(sys.modules[__name__], checker_name)
        ret = checker_func(request=request, mir_root=mir_root)
        if ret.code != CTLResponseCode.CTR_OK:
            logging.info("check failed: {}".format(item.name.lower()))
            return ret
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_nothing(request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_user_id(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    user_id = request.user_id
    if not (user_id and utils.check_valid_input_string(user_id)
            and len(user_id) == task_id_proto.IDProto.ID_LEN_USER_ID):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid user {}, abort".format(request.user_id))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_repo_id(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    repo_id = request.repo_id
    if not (repo_id and utils.check_valid_input_string(repo_id)
            and len(repo_id) == task_id_proto.IDProto.ID_LEN_REPO_ID):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid repo {}, abort".format(request.repo_id))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_task_id(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    task_id = request.task_id
    if not (task_id and utils.check_valid_input_string(task_id) and len(task_id) == task_id_proto.IDProto.ID_LENGTH):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid task {}, abort".format(task_id))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_singleton_op(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    task_id = request.singleton_op
    if not (task_id and utils.check_valid_input_string(task_id) and len(task_id) == task_id_proto.IDProto.ID_LENGTH):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid singleton_op {}, abort".format(task_id))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_dst_dataset_id(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    task_id = request.dst_dataset_id
    if not (task_id and utils.check_valid_input_string(task_id) and len(task_id) == task_id_proto.IDProto.ID_LENGTH):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid dst task {}, abort".format(task_id))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_his_task_id(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    task_id = request.his_task_id
    if not (task_id and utils.check_valid_input_string(task_id) and len(task_id) == task_id_proto.IDProto.ID_LENGTH):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid dst task {}, abort".format(task_id))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_guest_branches(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    guest_branches = request.guest_branches
    if not guest_branches:
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid guest branches {}, abort".format(guest_branches))
    for guest_branch in guest_branches:
        if not utils.check_valid_input_string(guest_branch) or len(guest_branch) != task_id_proto.IDProto.ID_LENGTH:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               "invalid guest branch {}, abort".format(guest_branch))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_taskinfo_ids(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    task_info_ids = request.req_get_task_info.task_ids
    if len(task_info_ids) == 0:
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, 'no task ids in request')
    for single_task_id in task_info_ids:
        if len(single_task_id) != task_id_proto.IDProto.ID_LENGTH:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               "invalid task_id {}".format(single_task_id))
    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_commit_message(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    commit_message = request.commit_message
    if not commit_message:
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid commit_message: {}, abort".format(commit_message))

    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_repo_root_exist(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    if not os.path.isdir(mir_root):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "mir_root not exist: {}, abort".format(mir_root))

    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_repo_root_not_exist(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    if os.path.isdir(mir_root):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "mir_root exist: {}, abort".format(mir_root))

    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_user_root_exist(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    user_root = os.path.basename(mir_root)
    if not os.path.isdir(user_root):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "user_root not exist: {}, abort".format(user_root))

    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_user_root_not_exist(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    user_root = os.path.basename(mir_root)
    if os.path.isdir(user_root):
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "user_root exist: {}, abort".format(user_root))

    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_in_dataset_ids(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    in_dataset_ids = request.in_dataset_ids
    if not in_dataset_ids:
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid in_dataset ids: {}".format(in_dataset_ids))

    return utils.make_general_response(CTLResponseCode.CTR_OK, "")


def _check_single_in_dataset_id(request: backend_pb2.GeneralReq, mir_root: str) -> backend_pb2.GeneralResp:
    in_dataset_ids = request.in_dataset_ids
    if not in_dataset_ids or len(in_dataset_ids) > 1:
        return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                           "invalid single in_dataset ids: {}".format(in_dataset_ids))

    return utils.make_general_response(CTLResponseCode.CTR_OK, "")
