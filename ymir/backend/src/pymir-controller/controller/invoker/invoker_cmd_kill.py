from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from proto import backend_pb2


class KillCMDInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[checker.Prerequisites.CHECK_USER_ID],)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_KILL:
            raise RuntimeError("Mismatched req_type")

        command = f"docker rm -f {self._request.executor_instance}"

        return utils.run_command(command)

    def _repr(self) -> str:
        return f"cmd_kill: user: {self._request.user_id}, kill executor_instance: {self._request.executor_instance}"
