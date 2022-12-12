import json
import logging
from typing import Optional

import sentry_sdk
import yaml

from controller.config import common_task as common_task_config
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
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

    def inspect_file_in_docker_image(self, filepath: str) -> Optional[str]:
        command = ['docker', 'run', '--rm', self._request.singleton_op, 'cat', filepath]
        config_response = utils.run_command(command)
        return self.convert_image_config(config_response.message)

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
            image_config = self.inspect_file_in_docker_image(image_config_path)
            if image_config:
                response.docker_image_config[image_type] = image_config

        # manifest
        serialized_manifest_config = self.inspect_file_in_docker_image(common_task_config.IMAGE_MANIFEST_PATH)
        manifest_config = json.loads(serialized_manifest_config) if serialized_manifest_config else {}
        response.enable_livecode = bool(manifest_config.get("enable_livecode", False))
        response.object_type = int(manifest_config.get("object_type", mir_cmd_pb.ObjectType.OT_DET_BOX))

        if len(response.docker_image_config) == 0:
            return utils.make_general_response(
                CTLResponseCode.DOCKER_IMAGE_ERROR,
                f"image {self._request.singleton_op} does not match any configuration",
            )

        return response
