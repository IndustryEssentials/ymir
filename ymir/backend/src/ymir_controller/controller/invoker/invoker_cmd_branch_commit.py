from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from proto import backend_pb2


class BranchCommitInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(invoker=self,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_COMMIT_MESSAGE,
                                     ])

    def invoke(self) -> backend_pb2.GeneralResp:
        # invoke command
        command = [utils.mir_executable(), 'commit', '--root', self._repo_root, '-m', self._request.commit_message]
        return utils.run_command(command)
