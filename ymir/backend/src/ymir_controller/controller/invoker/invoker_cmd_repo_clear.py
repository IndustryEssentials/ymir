from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, invoker_call, utils
from id_definition.error_codes import CTLResponseCode
from controller.invoker.invoker_cmd_branch_commit import BranchCommitInvoker
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

        request = self._request
        return invoker_call.make_invoker_cmd_call(
            invoker=BranchCommitInvoker,
            sandbox_root=self._sandbox_root,
            req_type=backend_pb2.RequestType.CMD_COMMIT,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=request.task_id,
            commit_message="Manually clear mir repo.",
        )
