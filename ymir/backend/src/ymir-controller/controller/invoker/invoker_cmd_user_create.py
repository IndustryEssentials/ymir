import pathlib

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, labels
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class UserCreateInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
            ],
            mir_root=self._repo_root,
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.USER_CREATE
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        # create user root
        repo_path = pathlib.Path(self._user_root)
        repo_path.mkdir(parents=True, exist_ok=True)
        # create label file
        labels.LabelFileHandler(self._user_root)

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message='')
