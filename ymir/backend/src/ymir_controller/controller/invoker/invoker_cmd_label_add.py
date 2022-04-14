from common_utils import labels
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils, checker
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class LabelAddInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_LABEL_ADD
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        response = utils.make_general_response(CTLResponseCode.CTR_OK, "")
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=labels.parse_labels_from_proto(self._request.label_collection),
                                              check_only=self._request.check_only)
        response.label_collection.CopyFrom(conflict_labels.to_proto())
        return response
