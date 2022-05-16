import subprocess
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class RepoCheckInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
                checker.Prerequisites.CHECK_REPO_ID,
                checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
            ],
            mir_root=self._repo_root,
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_REPO_CHECK
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

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
