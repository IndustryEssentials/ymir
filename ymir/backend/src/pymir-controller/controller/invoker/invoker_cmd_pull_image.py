import json
from typing import Optional

import sentry_sdk
import yaml

from controller.config import common_task as common_task_config
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, code
from controller.utils.app_logger import logger
from proto import backend_pb2


class ImageHandler(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[checker.Prerequisites.CHECK_USER_ID],)

    @staticmethod
    def get_image_config(raw_image_config: str) -> Optional[str]:
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

        config_result = dict()

        pull_command = f"docker pull {self._request.singleton_op}"
        pull_command_response = utils.run_command(pull_command)

        if pull_command_response.code != code.ResCode.CTR_OK:
            return utils.make_general_response(backend_pb2.RCode.RC_SERVICE_IMAGE_ERROR, pull_command_response.message)

        for image_type, image_config_path in common_task_config.IMAGE_CONFIG_PATH.items():
            config_command = f"docker run --rm {self._request.singleton_op} cat {image_config_path}"
            config_response = utils.run_command(config_command)
            config_result[image_type] = self.get_image_config(config_response.message)

        hash_command = f"docker images {self._request.singleton_op} --format {'{{.ID}}'} --no-trunc"
        response = utils.run_command(hash_command)
        response.hash_id = response.message
        response.message = json.dumps(config_result)

        return response

    def _repr(self) -> str:
        return f"image_pull: user: {self._request.user_id}, image_name: {self._request.singleton_op}"
