import os
from typing import Dict, List, Optional, Tuple
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskModelImportingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        model_importing_request = request.req_create_task.model_importing
        model_package_path = model_importing_request.model_package_path
        if not os.path.isfile(model_package_path):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"file not exists: {model_package_path}")

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def register_subtasks(cls) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_import, 1.0)]

    @classmethod
    def subtask_invoke_import(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, previous_subtask_id: Optional[str]) -> backend_pb2.GeneralResp:
        model_importing_request = request.req_create_task.model_importing
        model_package_path = model_importing_request.model_package_path

        cmd = [
            utils.mir_executable(), 'models', '--root', repo_root, '--package-path', model_package_path, '-w',
            subtask_workdir, '--dst-rev', f"{subtask_id}@{subtask_id}", '--model-location',
            assets_config["modelsuploadlocation"]
        ]
        return utils.run_command(cmd)
