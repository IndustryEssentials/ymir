import logging
import os
from typing import Dict, List
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskModelImportingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        model_importing_request = request.req_create_task.model_importing
        logging.info(f"model_importing_request: {model_importing_request}")
        model_package_path = model_importing_request.model_package_path
        if not os.path.isfile(model_package_path):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"file not exists: {model_package_path}")

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0]

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        model_importing_request = request.req_create_task.model_importing
        model_package_path = model_importing_request.model_package_path

        model_importing_response = cls.model_importing_cmd(repo_root=repo_root,
                                                           model_package_path=model_package_path,
                                                           task_id=subtask_id,
                                                           work_dir=subtask_workdir,
                                                           model_location=assets_config["modelsuploadlocation"])

        return model_importing_response

    @classmethod
    def model_importing_cmd(cls, repo_root: str, model_package_path: str, task_id: str, work_dir: str,
                            model_location: str) -> backend_pb2.GeneralResp:
        cmd = [
            utils.mir_executable(), 'models', '--root', repo_root, '--package-path', model_package_path,
            '-w', work_dir, '--dst-rev', f"{task_id}@{task_id}", '--model-location', model_location
        ]
        return utils.run_command(cmd)
