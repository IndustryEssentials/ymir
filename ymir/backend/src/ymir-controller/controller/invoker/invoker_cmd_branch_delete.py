from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from proto import backend_pb2


class BranchDeleteInvoker(BaseMirControllerInvoker):
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
        if self._request.req_type != backend_pb2.CMD_BRANCH_DEL:
            raise RuntimeError("Mismatched req_type")

        force_flag = "-D" if self._request.force else "-d"
        command = "cd {0} && {1} branch {2} {3}".format(self._repo_root, utils.mir_executable(), force_flag,
                                                        self._request.singleton_op)
        return utils.run_command(command)

    def _repr(self) -> str:
        force_flag = "-D" if self._request.force else "-d"
        return "branch_delete user: {}, repo: {}, force_flag: {}, branch: {}".format(
            self._request.user_id, self._request.repo_id, force_flag, self._request.singleton_op)
