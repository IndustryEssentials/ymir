import logging
import os
from abc import ABC, abstractmethod

from google.protobuf import json_format

from common_utils import labels
from controller.utils import checker, errors, metrics, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class BaseMirControllerInvoker(ABC):
    """
    base class for all mir controller invokers \n

    Attributes:
        sandbox_root: root of sandbox dir of all users
        user_name/user_path: user unique id and corresponding root path
        repo_name/repo_path: repo unique id and corresponding root path
        task_id: unique task id, check ymir_proto.util for more infos.
        _request: grpc request
    """
    def __init__(self,
                 sandbox_root: str,
                 request: backend_pb2.GeneralReq,
                 assets_config: dict,
                 async_mode: bool = False,
                 work_dir: str = "") -> None:
        super().__init__()

        # check sandbox_root & task_id
        if not os.path.isdir(sandbox_root):
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED,
                                     f"sandbox root {sandbox_root} not found, abort.")
        ret = checker.check_invoker(invoker=self, prerequisites=[checker.Prerequisites.CHECK_TASK_ID])
        if (ret.code != CTLResponseCode.CTR_OK):
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED, f"task_id {request.task_id} error, abort.")
        self._request = request
        self._sandbox_root = sandbox_root
        self._task_id = request.task_id
        self._assets_config = assets_config
        self._async_mode = async_mode
        self._work_dir = work_dir or self._prepare_work_dir()

        # check user_id
        self._user_id = request.user_id
        self._user_root = ""
        self._label_storage_file = ""
        self._user_labels = None
        if self._user_id:
            ret = checker.check_invoker(invoker=self, prerequisites=[checker.Prerequisites.CHECK_USER_ID])
            if (ret.code != CTLResponseCode.CTR_OK):
                raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED,
                                         f"user_id {request.user_id} error, abort.")

            self._user_root = os.path.join(sandbox_root, self._user_id)
            self._label_storage_file = os.path.join(self._user_root, labels.default_labels_file_name())
            self._user_labels = labels.get_user_labels_from_storage(self._label_storage_file)

        # check repo_id
        self._repo_id = request.repo_id
        self._repo_root = ""
        if request.repo_id:
            if not self._user_id or not self._user_root:
                raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED, "repo id provided, but miss user id.")
            ret = checker.check_invoker(invoker=self, prerequisites=[checker.Prerequisites.CHECK_REPO_ID])
            if (ret.code != CTLResponseCode.CTR_OK):
                raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED,
                                         f"repo_id {request.repo_id} error, abort.")

            self._repo_id = request.repo_id
            self._repo_root = os.path.join(self._user_root, request.repo_id)

        self._send_request_metrics()

    def _send_request_metrics(self) -> None:
        # only record task.
        if self._request.req_type != backend_pb2.TASK_CREATE:
            return

        metrics_name = backend_pb2.RequestType.Name(self._request.req_type) + '.'
        metrics_name += backend_pb2.TaskType.Name(self._request.req_create_task.task_type)
        metrics.send_counter_metrics(metrics_name)

    # functions about invoke and pre_invoke
    @utils.time_it
    def server_invoke(self) -> backend_pb2.GeneralResp:
        logging.info(str(self))

        response = self.pre_invoke()
        if response.code != CTLResponseCode.CTR_OK:
            return response

        return self.invoke()

    @abstractmethod
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        pass

    @abstractmethod
    def invoke(self) -> backend_pb2.GeneralResp:
        pass

    def _need_work_dir(self) -> bool:
        raise NotImplementedError

    def _prepare_work_dir(self) -> str:
        if not self._need_work_dir():
            return ''

        # Prepare working dir.
        if self._request.req_type == backend_pb2.RequestType.TASK_CREATE:
            type_dir = backend_pb2.TaskType.Name(self._request.req_create_task.task_type)
        else:
            type_dir = backend_pb2.RequestType.Name(self._request.req_type)

        work_dir = os.path.join(self._sandbox_root, "work_dir", type_dir, self._request.task_id)
        os.makedirs(os.path.join(work_dir, "out"), exist_ok=True)

        return work_dir

    def __repr__(self) -> str:
        """show infos about this invoker and the request"""
        req_info = json_format.MessageToDict(self._request,
                                             preserving_proto_field_name=True,
                                             use_integers_for_enums=True)

        return (f" request: \n {req_info}\n assets_config: {self._assets_config}\n async_mode: {self._async_mode} \n"
                "work_dir: {self._work_dir}")
