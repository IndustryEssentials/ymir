import os
from typing import Dict, List, Optional, Tuple
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskCopyInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if len(request.in_dataset_ids) != 1:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"Invalid in_dataset_ids {request.in_dataset_ids}")

        copy_request = request.req_create_task.copy
        if not (copy_request.src_user_id and copy_request.src_repo_id):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message="Invalid src user and/or repo id")
        src_root = os.path.join(self._sandbox_root, copy_request.src_user_id, copy_request.src_repo_id)
        if not os.path.isdir(src_root):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"Invalid src root: {src_root}")
        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_copy, 1.0)]

    @classmethod
    def subtask_invoke_copy(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                            assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                            subtask_workdir: str, his_task_id: Optional[str],
                            in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        copy_request = request.req_create_task.copy
        src_root = os.path.join(sandbox_root, copy_request.src_user_id, copy_request.src_repo_id)
        copy_response = cls.copying_cmd(repo_root=repo_root,
                                        task_id=subtask_id,
                                        src_root=src_root,
                                        src_dataset_id=in_dataset_ids[0],
                                        work_dir=subtask_workdir,
                                        name_strategy_ignore=copy_request.name_strategy_ignore,
                                        drop_annotations=copy_request.drop_annotations)

        return copy_response

    @staticmethod
    def copying_cmd(repo_root: str, task_id: str, src_root: str, src_dataset_id: str, work_dir: str,
                    name_strategy_ignore: bool, drop_annotations: bool) -> backend_pb2.GeneralResp:
        copying_cmd_str = [
            utils.mir_executable(), 'copy', '--root', repo_root, '--src-root', src_root, '--dst-rev',
            f"{task_id}@{task_id}", '--src-revs', f"{src_dataset_id}@{src_dataset_id}", '-w', work_dir
        ]

        if name_strategy_ignore:
            copying_cmd_str.append('--ignore-unknown-types')
        if drop_annotations:
            copying_cmd_str.append('--drop-annotations')

        return utils.run_command(copying_cmd_str)
