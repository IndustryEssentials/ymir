import subprocess
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class RepoCheckInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(
            invoker=self,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
                checker.Prerequisites.CHECK_REPO_ID,
                checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
            ],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        command = [utils.mir_executable(), 'status', '--root', self._repo_root]
        result = subprocess.run(command, capture_output=True, text=True)
        if 'clean' in result.stdout:
            response.ops_ret = True
        elif 'dirty' in result.stdout:
            response.ops_ret = False
        else:
            raise RuntimeError("Cannot check status for mir_root {self._repo_root}\nresult: {result}")
        return response
