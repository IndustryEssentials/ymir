from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils
from common_utils import sandbox
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class SandboxVersionInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    def invoke(self) -> backend_pb2.GeneralResp:
        sandbox_info = sandbox.SandboxInfo(root=self._sandbox_root)

        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        response.sandbox_version = sandbox_info.src_ver

        return response
