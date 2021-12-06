import logging
import re

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from proto import backend_pb2


class LogInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_LOG:
            raise RuntimeError("Mismatched req_type")

        command = "cd {0} && {1} log".format(self._repo_root, utils.mir_executable())
        response = utils.run_command(command)

        if response.code == 0 and response.message:
            message_lines = response.message.splitlines()
            logging.info('message_lines: ', message_lines)
            log_components = []  # List[str]
            for line in message_lines:
                if re.fullmatch(r"^commit +[0-9a-z]{40}$", line):
                    # finds a new part
                    commit_id = line.split(" ")[-1]
                    log_component = "commit {}".format(commit_id)
                    log_components.append(log_component)
                else:
                    # belongs to previous part
                    log_component = log_components[-1]
                    log_component = "{}\n{}".format(log_component, line)
                    log_components[-1] = log_component
            response.ext_strs.extend(log_components)

        return response

    def _repr(self) -> str:
        return "log: user: {}, repo: {}".format(self._request.user_id, self._request.repo_id)
