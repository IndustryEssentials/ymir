from common_utils import labels
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils, checker
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class LabelGetInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(
            invoker=self,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        if not self._user_labels:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid _user_labels")

        expected_type = backend_pb2.RequestType.CMD_LABEL_GET
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        response = utils.make_general_response(CTLResponseCode.CTR_OK, "")
        response.label_collection.CopyFrom(labels.userlabels_to_proto(self._user_labels))
        return response

    def _parse_response(self, response: backend_pb2.GeneralResp) -> str:
        return f"LabelGet: {len(response.label_collection.labels)}, version: {response.label_collection.ymir_version}"
