from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, gpu_utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class GPUInfoInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[checker.Prerequisites.CHECK_USER_ID])

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_GPU_INFO_GET
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        available_gpus = gpu_utils.GPUInfo.get_available_gpus()

        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        response.available_gpu_counts = len(available_gpus)

        return response
