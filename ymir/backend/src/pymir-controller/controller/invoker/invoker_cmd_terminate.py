from controller.config import label_task as label_task_config
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.label_model.label_studio import LabelStudio
from controller.utils import checker, utils, code
from controller.utils.redis import rds
from proto import backend_pb2


class CMDTerminateInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[checker.Prerequisites.CHECK_USER_ID],)

    def get_project_id_by_task_id(self, task_id: str) -> int:
        content = rds.hget(label_task_config.MONITOR_MAPPING_KEY, task_id)
        if content is None:
            raise ValueError("error! get project id: {} by task id{task_id}")
        return content["project_id"]  # type: ignore

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_TERMINATE:
            raise RuntimeError(f"Mismatched req_type CMD_TERMINATE: {self._request.req_type}")

        if self._request.terminated_task_type in [
            backend_pb2.TaskType.TaskTypeTraining,
            backend_pb2.TaskType.TaskTypeMining,
        ]:
            command = f"docker rm -f {self._request.executor_instance}"
            utils.run_command(command)
        elif self._request.terminated_task_type == backend_pb2.TaskType.TaskTypeLabel:
            project_id = self.get_project_id_by_task_id(self._request.executor_instance)
            LabelStudio().delete_unlabeled_task(project_id)

        return utils.make_general_response(code.ResCode.CTR_OK, "")

    def _repr(self) -> str:
        return f"cmd_terminate: user: {self._request.user_id}, terminate executor_instance: {self._request.executor_instance}"
