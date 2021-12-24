from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, gpu_utils, code
from proto import backend_pb2


class GPUInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[checker.Prerequisites.CHECK_USER_ID],)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_GPU_GET:
            raise RuntimeError("Mismatched req_type")

        free_gpus = gpu_utils.GPUInfo.get_available_gpus()

        return utils.make_general_response(code.ResCode.CTR_OK, str(len(free_gpus)))

    def _repr(self) -> str:
        return f"gpu: user: {self._request.user_id}"
