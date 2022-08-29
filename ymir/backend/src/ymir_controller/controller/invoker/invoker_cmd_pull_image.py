import json
import logging
from typing import Optional

import sentry_sdk
import yaml

from controller.config import common_task as common_task_config
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class ImageHandler(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(invoker=self, prerequisites=[checker.Prerequisites.CHECK_USER_ID])

    @staticmethod
    def convert_image_config(raw_image_config: str) -> Optional[str]:
        try:
            image_config = yaml.safe_load(raw_image_config)
            if not isinstance(image_config, dict):
                raise ValueError(f"raw image config error: {raw_image_config}")
        except Exception:
            error_message = f"raw image config error: {raw_image_config}"
            logging.error(error_message)
            sentry_sdk.capture_message(error_message)
            return None

        return json.dumps(image_config)

    def invoke(self) -> backend_pb2.GeneralResp:
        check_image_command = ['docker', 'image', 'inspect', self._request.singleton_op, '--format', 'ignore_me']
        check_response = utils.run_command(check_image_command)
        if check_response.code != CTLResponseCode.CTR_OK:
            pull_command = ['docker', 'pull', self._request.singleton_op]
            pull_command_response = utils.run_command(
                cmd=pull_command,
                error_code=CTLResponseCode.DOCKER_IMAGE_ERROR,
            )
            if pull_command_response.code != CTLResponseCode.CTR_OK:
                return pull_command_response

        hash_command = ['docker', 'images', self._request.singleton_op, '--format', '{{.ID}}']
        response = utils.run_command(hash_command)
        response.hash_id = response.message.strip()

        for image_type, image_config_path in common_task_config.IMAGE_CONFIG_PATH.items():
            config_command = ['docker', 'run', '--rm', self._request.singleton_op, 'cat', image_config_path]
            config_response = utils.run_command(config_command)
            image_config = self.convert_image_config(config_response.message)
            if image_config:
                response.docker_image_config[image_type] = image_config

        # livecode
        config_command = [
            'docker', 'run', '--rm', self._request.singleton_op,
            'cat', common_task_config.IMAGE_LIVECODE_CONFIG_PATH
        ]
        config_response = utils.run_command(config_command)
        livecode_config = self.convert_image_config(config_response.message)
        if livecode_config:
            response.enable_livecode = True

        if len(response.docker_image_config) == 0:
            return utils.make_general_response(
                CTLResponseCode.DOCKER_IMAGE_ERROR,
                f"image {self._request.singleton_op} does not match any configuration",
            )

        return response
