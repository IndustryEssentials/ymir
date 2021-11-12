from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from ymir.protos import mir_controller_service_pb2 as mirsvrpb


class BranchCommitInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> mirsvrpb.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_COMMIT_MESSAGE,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> mirsvrpb.GeneralResp:
        if self._request.req_type != mirsvrpb.CMD_COMMIT:
            raise RuntimeError("Mismatched req_type")

        # invoke command
        command = "cd {0} && {1} commit -m '{2}'".format(self._repo_root, utils.mir_executable(),
                                                         self._request.commit_message)
        return utils.run_command(command)

    def _repr(self) -> str:
        return "commit: user: {}, repo: {}, message: {}".format(self._request.user_id, self._request.repo_id,
                                                                self._request.commit_message)
