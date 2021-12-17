import json
from typing import Optional

import sentry_sdk
import yaml

from controller.config import IMAGE_INFER_CONFIG_PATH, IMAGE_MINING_CONFIG_PATH, IMAGE_TRAINING_CONFIG_PATH
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

        if self._request.operate_task_type == backend_pb2.TaskType.TaskTypeTraining:
            image_config_path = IMAGE_TRAINING_CONFIG_PATH
        elif self._request.operate_task_type == backend_pb2.TaskType.TaskTypeMining:
            image_config_path = IMAGE_MINING_CONFIG_PATH
        elif self._request.operate_task_type == backend_pb2.TaskType.TaskTypeInfer:
            image_config_path = IMAGE_INFER_CONFIG_PATH
        else:
            raise ValueError(f"operate_task_type error:{self._request.operate_task_type}")

        config_command = f"docker run --rm {self._request.singleton_op} cat {image_config_path}"
        config_response = utils.run_command(config_command)

        image_config = self.get_image_config(config_response.message)
        if image_config:
            hash_command = f"docker images {self._request.singleton_op} --format {'{{.ID}}'} --no-trunc"
            hash_response = utils.run_command(hash_command)

            response = utils.make_general_response(code.ResCode.CTR_OK, config_response.message)
            response.hash_id = hash_response.message
        else:
            response = utils.make_general_response(backend_pb2.RCode.RC_SERVICE_IMAGE_ERROR, config_response.message)

        return response

    def _repr(self) -> str:
        return f"image_pull: user: {self._request.user_id}, image_name: {self._request.singleton_op}"
