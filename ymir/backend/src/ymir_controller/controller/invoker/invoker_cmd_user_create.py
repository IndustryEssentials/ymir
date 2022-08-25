import os

from common_utils import labels
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class UserCreateInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(
            invoker=self,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
            ],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        # create user root
        os.makedirs(self._user_root, exist_ok=True)
        # create label file
        labels.create_empty(label_storage_file=self._label_storage_file)

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message='')
