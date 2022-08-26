from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, gpu_utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class GPUInfoInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(invoker=self, prerequisites=[checker.Prerequisites.CHECK_USER_ID])

    def invoke(self) -> backend_pb2.GeneralResp:
        available_gpus = gpu_utils.GPUInfo.get_available_gpus()

        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        response.available_gpu_counts = len(available_gpus)

        return response
