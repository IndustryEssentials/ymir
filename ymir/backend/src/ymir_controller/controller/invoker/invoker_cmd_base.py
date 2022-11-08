import logging
import os
from abc import ABC, abstractmethod

from google.protobuf.json_format import MessageToDict
from google.protobuf.text_format import MessageToString

from common_utils import labels
from controller.utils import errors, metrics, utils
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
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
            self._user_root = os.path.join(sandbox_root, self._user_id)
            self._label_storage_file = os.path.join(self._user_root, labels.ids_file_name())
            self._user_labels = labels.UserLabels(storage_file=self._label_storage_file)

        # check repo_id
        self._repo_id = request.repo_id
        self._repo_root = ""
        if request.repo_id:
            if not self._user_id or not self._user_root:
                raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED, "repo id provided, but miss user id.")

            self._repo_id = request.repo_id
            self._repo_root = os.path.join(self._user_root, request.repo_id)

        self._send_request_metrics()

    def _send_request_metrics(self) -> None:
        # only record task.
        if self._request.req_type != backend_pb2.TASK_CREATE:
            return

        metrics_name = backend_pb2.RequestType.Name(self._request.req_type) + '.'
        metrics_name += mir_cmd_pb.TaskType.Name(self._request.req_create_task.task_type)
        metrics.send_counter_metrics(metrics_name)

    # functions about invoke and pre_invoke
    @utils.time_it
    def server_invoke(self) -> backend_pb2.GeneralResp:
        logging.info(str(self))

        response = self.pre_invoke()
        if response.code != CTLResponseCode.CTR_OK:
            logging.info(f"pre_invoke fails: {response}")
            return response

        response = self.invoke()
        logging.info(self._parse_response(response))
        return response

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
            type_dir = mir_cmd_pb.TaskType.Name(self._request.req_create_task.task_type)
        else:
            type_dir = backend_pb2.RequestType.Name(self._request.req_type)

        work_dir = os.path.join(self._sandbox_root, "work_dir", type_dir, self._request.task_id)
        os.makedirs(os.path.join(work_dir, "out"), exist_ok=True)

        return work_dir

    def __repr__(self) -> str:
        """show infos about this invoker and the request"""
        request = self._request
        if request.req_type in [
                backend_pb2.RequestType.CMD_GPU_INFO_GET,
                backend_pb2.RequestType.CMD_LABEL_ADD,
                backend_pb2.RequestType.CMD_LABEL_GET,
                backend_pb2.RequestType.CMD_PULL_IMAGE,
                backend_pb2.RequestType.CMD_REPO_CHECK,
                backend_pb2.RequestType.CMD_REPO_CLEAR,
                backend_pb2.RequestType.CMD_TERMINATE,
                backend_pb2.RequestType.CMD_VERSIONS_GET,
        ]:
            return f"task_id: {request.task_id} req_type: {request.req_type}"

        pb_dict = MessageToDict(request, preserving_proto_field_name=True, use_integers_for_enums=True)
        return (f"{self.__class__}\n request: {pb_dict}\n assets_config: {self._assets_config}\n"
                f" async_mode: {self._async_mode}\n work_dir: {self._work_dir}")

    def _parse_response(self, response: backend_pb2.GeneralResp) -> str:
        return f"task id: {self._request.task_id} response: {MessageToString(response, as_one_line=True)}"
