from controller import config
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.label_model.label_studio import LabelStudio
from controller.utils import checker, utils, code
from controller.utils.redis import rds
from proto import backend_pb2


class FinishLabelTaskInvoker(BaseMirControllerInvoker):
    def get_project_id_by_task_id(self, task_id: str) -> int:
        content = rds.hget(config.MONITOR_MAPPING_KEY, task_id)
        if content is None:
            raise ValueError("error! get project id: {} by task id{task_id}")
        return content["project_id"]  # type: ignore

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
                checker.Prerequisites.CHECK_REPO_ID,
                checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
            ],
            mir_root=self._repo_root,
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        project_id = self.get_project_id_by_task_id(self._request.executor_instance)
        LabelStudio().delete_unlabeled_task(project_id)

        return utils.make_general_response(code.ResCode.CTR_OK, "")

    def _repr(self) -> str:
        return f"cmd_finish_label_task: user: {self._request.user_id}, task_id: {self._task_id}"
