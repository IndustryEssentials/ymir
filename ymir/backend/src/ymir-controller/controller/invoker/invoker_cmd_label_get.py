from typing import List

from google.protobuf import json_format

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils, checker, labels
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class LabelGetInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
        )

    @staticmethod
    def generate_response(all_labels: List[labels.SingleLabel]) -> backend_pb2.GeneralResp:
        response = utils.make_general_response(CTLResponseCode.CTR_OK, "")
        for label in all_labels:
            label_pb = backend_pb2.Label()
            json_format.ParseDict(label.dict(), label_pb)
            response.label_collection.labels.append(label_pb)

        return response

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_LABEL_GET
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        label_handler = labels.LabelFileHandler(self._user_root)
        all_labels = label_handler.get_all_labels()

        return self.generate_response(all_labels)
