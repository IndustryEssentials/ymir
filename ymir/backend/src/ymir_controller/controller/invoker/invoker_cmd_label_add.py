from common_utils import labels
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils, checker
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class LabelAddInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(
            invoker=self,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        response = utils.make_general_response(CTLResponseCode.CTR_OK, "")
        user_labels = labels.UserLabels(storage_file=self._label_storage_file)
        conflict_labels = user_labels.upsert_labels(
            new_labels=labels.parse_labels_from_proto(self._request.label_collection),
            check_only=self._request.check_only
        )
        response.label_collection.CopyFrom(labels.userlabels_to_proto(conflict_labels))
        return response

    def _parse_response(self, response: backend_pb2.GeneralResp) -> str:
        return f"LabelAdd conflict: {len(response.label_collection.labels)}, {response.label_collection.ymir_version}"
