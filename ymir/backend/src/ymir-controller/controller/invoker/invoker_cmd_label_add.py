from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils, checker, labels
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
        label_handler = labels.LabelFileHandler(self._user_root)
        conflict_rows = label_handler.merge_labels(self._request.private_labels, self._request.check_only)
        for row in conflict_rows:
            label = backend_pb2.Label()
            label.id = -1
            label.name = row[0]
            label.aliases.extend(row[1:])
            response.label_collection.labels.append(label)

        return response
