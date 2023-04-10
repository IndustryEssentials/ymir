import os
from typing import Dict, List, Optional, Tuple

from common_utils.percent_log_util import LogState, PercentLogHandler
from common_utils.labels import UserLabels
from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class ImageHandler(TaskBaseInvoker):
    @classmethod
    def need_index_repo(cls) -> bool:
        return False

    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        return checker.check_invoker(invoker=self, prerequisites=[checker.Prerequisites.CHECK_USER_ID])

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_pull_image, 1.0)]

    @classmethod
    def subtask_invoke_pull_image(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                                  assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                                  subtask_workdir: str, his_task_id: Optional[str],
                                  in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        check_image_command = ['docker', 'image', 'inspect', request.singleton_op, '--format', 'ignore_me']
        check_response = utils.run_command(check_image_command)
        if check_response.code == CTLResponseCode.CTR_OK:
            return check_response

        pull_command = ['docker', 'pull', request.singleton_op]
        pull_response = utils.run_command(
            cmd=pull_command,
            error_code=CTLResponseCode.DOCKER_IMAGE_ERROR,
        )

        PercentLogHandler.write_percent_log(
            log_file=os.path.join(subtask_workdir, "out", "monitor.txt"),
            tid=subtask_id,
            percent=1.0,
            state=LogState.DONE if pull_response.code == CTLResponseCode.CTR_OK else LogState.ERROR,
            error_code=pull_response.code,
            error_message=pull_response.message)

        return pull_response
