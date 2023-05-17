import os
from typing import Dict, List, Optional, Tuple
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CMDResponseCode, CTLResponseCode
from proto import backend_pb2


class TaskImportModelInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        import_model_request = request.req_create_task.import_model
        model_package_path = import_model_request.model_package_path
        if not os.path.isfile(model_package_path):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"file not exists: {model_package_path}")

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_import, 1.0)]

    @classmethod
    def subtask_invoke_import(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, his_task_id: Optional[str],
                              in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        import_model_request = request.req_create_task.import_model
        model_package_path = import_model_request.model_package_path

        cmd = [
            utils.mir_executable(), 'models', '--root', repo_root, '--package-path', model_package_path, '-w',
            subtask_workdir, '--dst-rev', f"{subtask_id}@{subtask_id}", '--model-location',
            assets_config["modelsuploadlocation"]
        ]
        return utils.run_command(cmd, error_code=CMDResponseCode.RC_CMD_INVALID_MODEL)
