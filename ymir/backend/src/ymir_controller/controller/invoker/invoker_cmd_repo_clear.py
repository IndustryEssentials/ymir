from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class RepoClearInvoker(BaseMirControllerInvoker):
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
        expected_type = backend_pb2.RequestType.CMD_REPO_CLEAR
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        command = [utils.mir_executable(), 'commit', '--root', self._repo_root, '-m', 'manually clear repo.']
        return utils.run_command(command)
