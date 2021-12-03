import logging
import os
from abc import ABC, abstractmethod

from google.protobuf import json_format

from controller.utils import code, checker
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
                 async_mode: bool = False) -> None:
        super().__init__()

        # check sandbox_root
        if not os.path.isdir(sandbox_root):
            raise RuntimeError(f"sandbox root {sandbox_root} not found, abort")
        self._sandbox_root = sandbox_root

        ret = checker.check_request(request=request, prerequisites=[checker.Prerequisites.CHECK_TASK_ID])
        if (ret.code != code.ResCode.CTR_OK):
            raise RuntimeError(f"task_id {request.task_id} error, abort")
        self._task_id = request.task_id

        # check user_id
        user_id = request.user_id
        if user_id:
            self._user_id = user_id
            self._user_root = os.path.join(sandbox_root, user_id)

        # check repo_id
        repo_id = request.repo_id
        if user_id and repo_id:
            self._repo_id = repo_id
            self._repo_root = os.path.join(self._user_root, repo_id)

        self._request = request
        self._assets_config = assets_config
        self._async_mode = async_mode
        self._work_dir = self.prepare_work_dir()

    # functions about invoke and pre_invoke
    def server_invoke(self) -> backend_pb2.GeneralResp:
        logging.info(str(self))

        response = self.pre_invoke()
        if response.code != code.ResCode.CTR_OK:
            return response

        return self.invoke()

    @abstractmethod
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        pass

    @abstractmethod
    def invoke(self) -> backend_pb2.GeneralResp:
        pass

    def prepare_work_dir(self) -> str:
        # Prepare working dir.
        if self._request.req_type == backend_pb2.TASK_CREATE:
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

        return f"{self._repr()} \n request: \n {req_info}"

    @abstractmethod
    def _repr(self) -> str:
        raise NotImplementedError()
