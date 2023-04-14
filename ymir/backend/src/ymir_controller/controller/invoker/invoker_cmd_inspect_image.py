import json
import logging
import os
from typing import List, Optional, Tuple

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

        manifest_object_types = manifest_config.get("object_type", mir_cmd_pb.ObjectType.OT_DET_BOX)
        object_type_and_dirs: List[Tuple[int, str]] = []  # 1st: object_type, 2nd: template root dir
        if isinstance(manifest_object_types, list):
            object_type_and_dirs.extend([(x,
                                          os.path.join(common_task_config.IMAGE_CONFIG_ROOT,
                                                       common_task_config.IMAGE_CONFIG_DIR_NAMES[x]))
                                         for x in manifest_object_types])
        elif isinstance(manifest_object_types, int):
            object_type_and_dirs.append((manifest_object_types, common_task_config.IMAGE_CONFIG_ROOT))
        else:
            return utils.make_general_response(
                CTLResponseCode.DOCKER_IMAGE_ERROR,
                f"image {self._request.singleton_op} has invalid object types: {manifest_object_types}",
            )

        # templates
        task_types = [mir_cmd_pb.TaskTypeTraining, mir_cmd_pb.TaskTypeMining, mir_cmd_pb.TaskTypeInfer]
        for object_type, object_type_dir in object_type_and_dirs:
            for task_type in task_types:
                config_file_path = os.path.join(object_type_dir, common_task_config.IMAGE_CONFIG_FILE_NAMES[task_type])
                image_config = self._inspect_file_in_docker_image(docker_image_tag=self._request.singleton_op,
                                                                  filepath=config_file_path)
                if image_config:
                    response.docker_image_config[object_type].config[task_type] = image_config

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
