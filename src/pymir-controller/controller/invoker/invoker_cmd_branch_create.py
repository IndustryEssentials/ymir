from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from proto import backend_pb2


class BranchCreateInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_SINGLETON_OP,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_BRANCH_CREATE:
            raise RuntimeError("Mismatched req_type")

        branch_id = self._request.singleton_op
        command = "cd {0} && {1} checkout -b {2}".format(self._repo_root, utils.mir_executable(), branch_id)
        return utils.run_command(command)

    def _repr(self) -> str:
        return "checkout -b: user: {}, repo: {}, branch: {}".format(self._request.user_id, self._request.repo_id,
                                                                    self._request.singleton_op)
