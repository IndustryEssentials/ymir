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
    def convert_image_config(raw_image_config: str) -> Optional[str]:
        try:
            image_config = yaml.safe_load(raw_image_config)
            if not isinstance(image_config, dict):
                raise ValueError(f"raw image config error: {raw_image_config}")
        except Exception as e:
            error_message = f"raw image config error: {raw_image_config}"
            logger.error(error_message)
            sentry_sdk.capture_message(error_message)
            return None

        return json.dumps(image_config)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_PULL_IMAGE:
            raise RuntimeError("Mismatched req_type")

        check_image_command = f"docker image inspect {self._request.singleton_op} --format='ignore me'"
        check_response = utils.run_command(check_image_command)
        if check_response.code != code.ResCode.CTR_OK:
            pull_command = f"docker pull {self._request.singleton_op}"
            pull_command_response = utils.run_command(pull_command)
            if pull_command_response.code != code.ResCode.CTR_OK:
                return utils.make_general_response(
                    backend_pb2.RCode.RC_SERVICE_DOCKER_IMAGE_ERROR, pull_command_response.message
                )

        hash_command = f"docker images {self._request.singleton_op} --format {'{{.ID}}'}"
        response = utils.run_command(hash_command)
        response.hash_id = response.message.strip()

        for image_type, image_config_path in common_task_config.IMAGE_CONFIG_PATH.items():
            config_command = f"docker run --rm {self._request.singleton_op} cat {image_config_path}"
            config_response = utils.run_command(config_command)
            image_config = self.convert_image_config(config_response.message)
            if image_config:
                response.docker_image_config[image_type] = image_config

        return response

    def _repr(self) -> str:
        return f"image_pull: user: {self._request.user_id}, image_name: {self._request.singleton_op}"
