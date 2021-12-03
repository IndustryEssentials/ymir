"""
mir controller server that controls remote workspace (called sandbox here)
"""

import logging
from typing import Any, Dict

from controller.utils import utils
from controller.utils.code import ResCode
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2, backend_pb2_grpc


class MirControllerService(backend_pb2_grpc.mir_controller_serviceServicer):
    __slots__ = ("_sandbox_root", "_user_to_container_ids", "_docker_image_name")

    user_to_container_ids = {}  # type: Dict[str, str]

    def __init__(self, sandbox_root: str, assets_config: dict) -> None:
        self._sandbox_root = sandbox_root
        self._assets_config = assets_config

    @property
    def sandbox_root(self) -> str:
        return self._sandbox_root

    @property
    def assets_config(self) -> Dict:
        return self._assets_config

    def data_manage_request(self, request: backend_pb2.GeneralReq, context: Any) -> backend_pb2.GeneralResp:
        if request.req_type not in RequestTypeToInvoker:
            message = "unknown invoker for req_type: {}".format(request.req_type)  # type: str
            logging.error(message)
            return utils.make_general_response(ResCode.CTR_INVALID_SERVICE_REQ, message)

        invoker_class = RequestTypeToInvoker[request.req_type]
        # TODO:(xhuang) add try-catch process before release product.
        invoker = invoker_class(sandbox_root=self.sandbox_root,
                                request=request,
                                assets_config=self.assets_config,
                                async_mode=True)
        invoker_result = invoker.server_invoke()

        if isinstance(invoker_result, backend_pb2.GeneralResp):
            return invoker_result
        return utils.make_general_response(ResCode.CTR_SERVICE_UNKOWN_RESPONSE,
                                           "unknown result type: {}".format(type(invoker_result)))
