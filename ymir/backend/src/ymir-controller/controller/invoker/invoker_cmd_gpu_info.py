from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, gpu_utils, code
from proto import backend_pb2


class GPUInfoInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[checker.Prerequisites.CHECK_USER_ID],)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_GPU_INFO_GET:
            raise RuntimeError(f"Mismatched req_type {self._request.req_type}")

        available_gpus = gpu_utils.GPUInfo.get_available_gpus()

        response = backend_pb2.GeneralResp()
        response.code = code.ResCode.CTR_OK
        response.available_gpu_counts = len(available_gpus)

        return response

    def _repr(self) -> str:
        return f"gpu: user: {self._request.user_id}"
