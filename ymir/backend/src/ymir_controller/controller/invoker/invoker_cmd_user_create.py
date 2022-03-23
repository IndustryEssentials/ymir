import pathlib

from common_utils import labels
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class UserCreateInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
            ],
            mir_root='',
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.USER_CREATE
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        # create user root
        pathlib.Path(self._user_root).mkdir(parents=True, exist_ok=True)
        # create label file
        labels.create_empty(label_storage_file=self._label_storage_file)

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message='')
