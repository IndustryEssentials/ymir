import os
import pathlib

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, labels
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class InitInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
                checker.Prerequisites.CHECK_REPO_ID,
                checker.Prerequisites.CHECK_REPO_ROOT_NOT_EXIST,
            ],
            mir_root=self._repo_root,
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = [backend_pb2.RequestType.CMD_INIT, backend_pb2.RequestType.REPO_CREATE]
        if self._request.req_type not in expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        repo_path = pathlib.Path(self._repo_root)
        repo_path.mkdir(parents=True, exist_ok=True)

        label_handler = labels.LabelFileHandler(self._user_root)
        label_file = label_handler.get_label_file_path()
        link_dst_file = os.path.join(self._repo_root, os.path.basename(label_file))
        os.link(label_file, link_dst_file)

        command = f"cd {str(repo_path)} && {utils.mir_executable()} init"

        return utils.run_command(
            cmd=command,
            error_code=CTLResponseCode.INVOKER_INIT_ERROR,
        )
