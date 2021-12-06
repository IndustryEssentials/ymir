from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from proto import backend_pb2


class BranchListInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_BRANCH_LIST:
            raise RuntimeError("Mismatched req_type")

        command = "cd {} && {} branch".format(self._repo_root, utils.mir_executable())
        response = utils.run_command(command)

        if response.code == 0 and response.message:
            message_lines = response.message.splitlines()
            for message_line in message_lines:
                # remove empty lines
                message_line = message_line.strip()
                if message_line:
                    response.ext_strs.append(message_line)
            response.message = ""

        return response

    def _repr(self) -> str:
        return "branch list: user: {}, repo: {}".format(self._request.user_id, self._request.repo_id)
