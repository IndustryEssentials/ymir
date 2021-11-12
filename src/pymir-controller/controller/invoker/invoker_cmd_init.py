import os

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from ymir.protos import mir_controller_service_pb2 as mirsvrpb


class InitInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> mirsvrpb.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_NOT_EXIST,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> mirsvrpb.GeneralResp:
        if self._request.req_type not in [mirsvrpb.CMD_INIT, mirsvrpb.REPO_CREATE]:
            raise RuntimeError("Mismatched req_type")

        os.makedirs(self._user_root, exist_ok=True)
        command = "cd {0} && mkdir {1} && cd {1} && {2} init".format(self._user_root, self._request.repo_id,
                                                                     utils.mir_executable())  # type: str
        return utils.run_command(command)

    def _repr(self) -> str:
        return "init: user: {}, repo: {}".format(self._request.user_id, self._request.repo_id)
