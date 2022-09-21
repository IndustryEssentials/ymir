from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils
from common_utils.sandbox_util import detect_sandbox_src_ver
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class SandboxVersionInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    def invoke(self) -> backend_pb2.GeneralResp:
        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        response.sandbox_version = detect_sandbox_src_ver(self._sandbox_root)

        return response
