from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import code, utils, checker, labels
from proto import backend_pb2
from typing import List


class LabelGetInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
        )

    @staticmethod
    def generate_response(all_labels: List[List]) -> backend_pb2.GeneralResp:
        response = utils.make_general_response(code.ResCode.CTR_OK, "")
        result = [",".join(one_row_labels) for one_row_labels in all_labels]
        response.csv_labels.extend(result)

        return response

    def invoke(self) -> backend_pb2.GeneralResp:
        label_handler = labels.LabelFileHandler(self._user_root)
        all_labels = label_handler.get_all_labels(with_reserve=False)

        return self.generate_response(all_labels)

    def _repr(self) -> str:
        return f"cmd_labels_get: user: {self._request.user_id}, task_id: {self._task_id} "
