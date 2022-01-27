import logging
import os
from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskCopyInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        copy_request = request.req_create_task.copy
        logging.info(f"copy_request: {copy_request}")
        if not (copy_request.src_user_id and copy_request.src_repo_id):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message="Invalid src user and/or repo id")
        src_root = os.path.join(sandbox_root, copy_request.src_user_id, copy_request.src_repo_id)
        if not os.path.isdir(src_root):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"Invalid src root: {src_root}")
        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def subtask_count(cls) -> int:
        return 1

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        copy_request = request.req_create_task.copy
        src_root = os.path.join(sandbox_root, copy_request.src_user_id, copy_request.src_repo_id)
        copy_response = cls.copying_cmd(repo_root=repo_root,
                                        task_id=subtask_id,
                                        src_root=src_root,
                                        src_dataset_id=copy_request.src_dataset_id,
                                        work_dir=subtask_workdir,
                                        name_strategy_ignore=copy_request.name_strategy_ignore)

        return copy_response

    @staticmethod
    def copying_cmd(repo_root: str, task_id: str, src_root: str, src_dataset_id: str, work_dir: str,
                    name_strategy_ignore: bool) -> backend_pb2.GeneralResp:
        copying_cmd_str = (f"cd {repo_root} && mir copy --src-root {src_root} --dst-rev {task_id}@{task_id} "
                           f"--src-revs {src_dataset_id}@{src_dataset_id} -w {work_dir}")

        if name_strategy_ignore:
            copying_cmd_str += " --ignore-unknown-types"

        return utils.run_command(copying_cmd_str)
