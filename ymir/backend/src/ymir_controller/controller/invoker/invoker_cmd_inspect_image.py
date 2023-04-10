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


class CmdInspectImageInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(invoker=self, prerequisites=[checker.Prerequisites.CHECK_USER_ID])

    def invoke(self) -> backend_pb2.GeneralResp:
        hash_command = ['docker', 'images', self._request.singleton_op, '--format', '{{.ID}}']
        response = utils.run_command(hash_command)
        response.hash_id = response.message.strip()

        # manifest
        serialized_manifest_config = self._inspect_file_in_docker_image(docker_image_tag=self._request.singleton_op,
                                                                        filepath=common_task_config.IMAGE_MANIFEST_PATH)
        manifest_config = json.loads(serialized_manifest_config) if serialized_manifest_config else {}
        response.enable_livecode = bool(manifest_config.get("enable_livecode", False))
        response.object_type = int(manifest_config.get("object_type", mir_cmd_pb.ObjectType.OT_DET_BOX))

        # templates
        for image_type, image_config_path in common_task_config.IMAGE_CONFIG_PATH.items():
            image_config = self._inspect_file_in_docker_image(docker_image_tag=self._request.singleton_op,
                                                              filepath=image_config_path)
            if image_config:
                response.docker_image_config[image_type] = image_config

        if len(response.docker_image_config) == 0:
            return utils.make_general_response(
                CTLResponseCode.DOCKER_IMAGE_ERROR,
                f"image {self._request.singleton_op} does not match any configuration",
            )

        return response

    @classmethod
    def _inspect_file_in_docker_image(cls, docker_image_tag: str, filepath: str) -> Optional[str]:
        command = ['docker', 'run', '--rm', docker_image_tag, 'cat', filepath]
        config_response = utils.run_command(command)

        try:
            image_config = yaml.safe_load(config_response.message)
            if not isinstance(image_config, dict):
                raise ValueError(f"raw image config error: {config_response.message}")
        except Exception:
            error_message = f"raw image config error: {config_response.message}"
            logging.error(error_message)
            sentry_sdk.capture_message(error_message)
            return None

        return json.dumps(image_config)
