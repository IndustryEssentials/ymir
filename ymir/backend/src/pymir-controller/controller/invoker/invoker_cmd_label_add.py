from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import code, utils, checker, labels
from proto import backend_pb2


class LabelAddInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        response = utils.make_general_response(code.ResCode.CTR_OK, "")
        label_handler = labels.LabelFileHandler(self._user_root)
        conflict_rows = label_handler.merge_labels(self._request.private_labels, self._request.check_only)
        response.csv_labels.extend([",".join(row) for row in conflict_rows])

        return response

    def _repr(self) -> str:
        return (
            f"cmd_labels_add: user: {self._request.user_id}, task_id: {self._task_id} "
            f"private_labels: {self._request.private_labels}"
        )
