from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, invoker_call
from id_definition.error_codes import CTLResponseCode
from controller.invoker.invoker_cmd_branch_commit import BranchCommitInvoker
from controller.invoker.invoker_cmd_repo_check import RepoCheckInvoker
from proto import backend_pb2


class RepoClearInvoker(BaseMirControllerInvoker):
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
        request = self._request
        check_ret = invoker_call.make_invoker_cmd_call(
            invoker=RepoCheckInvoker,
            sandbox_root=self._sandbox_root,
            req_type=backend_pb2.RequestType.CMD_REPO_CHECK,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=request.task_id,
        )
        # check failed, or repo is clean.
        if check_ret.code != CTLResponseCode.CTR_OK or check_ret.ops_ret:
            return check_ret

        return invoker_call.make_invoker_cmd_call(
            invoker=BranchCommitInvoker,
            sandbox_root=self._sandbox_root,
            req_type=backend_pb2.RequestType.CMD_COMMIT,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=request.task_id,
            commit_message="Manually clear mir repo.",
        )
