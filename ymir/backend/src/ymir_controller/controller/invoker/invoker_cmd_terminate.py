import logging

import sentry_sdk

from controller.config import label_task as label_task_config
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from controller.utils.redis import rds
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2


class CMDTerminateInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(
            invoker=self,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
        )

    def get_project_id_by_task_id(self, task_id: str) -> int:
        content = rds.hget(label_task_config.MONITOR_MAPPING_KEY, task_id)
        if content is None:
            raise ValueError("error! get project id: {} by task id{task_id}")
        return content["project_id"]  # type: ignore

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.terminated_task_type in [
                mir_cmd_pb.TaskType.TaskTypeTraining,
                mir_cmd_pb.TaskType.TaskTypeMining,
                mir_cmd_pb.TaskType.TaskTypeDatasetInfer,
        ]:
            container_command = ['docker', 'rm', '-f', self._request.executant_name]
            container_response = utils.run_command(container_command)
            if container_response.code != CTLResponseCode.CTR_OK:
                logging.warning(container_response.message)
                sentry_sdk.capture_message(container_response.message)
                return container_response
        elif self._request.terminated_task_type == mir_cmd_pb.TaskType.TaskTypeLabel:
            project_id = self.get_project_id_by_task_id(self._request.executant_name)
            label_instance = utils.create_label_instance()
            label_instance.delete_unlabeled_task(project_id)
        else:
            logging.info(f"Do nothing to terminate task_type:{self._request.req_type}")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "successful terminate")
