from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, code
from proto import backend_pb2
import yaml
import json
from controller.config import IMAGE_INFER_CONFIG_PATH, IMAGE_MINING_CONFIG_PATH, IMAGE_TRAINING_CONFIG_PATH
from controller.utils.app_logger import logger
import sentry_sdk


class ImageHandler(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[checker.Prerequisites.CHECK_USER_ID],)

    @staticmethod
    def get_image_config(raw_image_config):
        image_config = yaml.safe_load(raw_image_config)
        if not isinstance(image_config, dict):
            error_message = f"raw image config error: {raw_image_config}"
            logger.error(error_message)
            sentry_sdk.capture_message(error_message)
            return None

        return json.dumps(image_config)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_PULL_IMAGE:
            raise RuntimeError("Mismatched req_type")

        command = f"docker run --rm {self._request.singleton_op} cat {IMAGE_TRAINING_CONFIG_PATH}"

        response = utils.run_command(command)

        image_config = self.get_image_config(response.message)
        if not image_config:
            return utils.make_general_response(code.ResCode.CTR_ERROR_UNKNOWN, response.message)
        else:
            return utils.make_general_response(code.ResCode.CTR_OK, image_config)

    def _repr(self) -> str:
        return f"cmd_kill: user: {self._request.user_id}, kill executor_instance: {self._request.executor_instance}"
