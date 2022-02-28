from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import invoker_call, revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskMfsInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        # train_request = request.req_create_task.training
        # if not train_request.in_dataset_types:
        #     return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid dataset_types")

        # # store executor config in task_0 work_dir
        # subtask_work_dir_0 = self.subtask_work_dir(self._work_dir, utils.sub_task_id(self._task_id, 0))
        # output_config_file = self.gen_executor_config_path(subtask_work_dir_0)
        # gpu_lock_ret = self.gen_executor_config_lock_gpus(
        #     repo_root=self._repo_root,
        #     req_executor_config=request.docker_image_config,
        #     in_class_ids=train_request.in_class_ids,
        #     output_config_file=output_config_file,
        # )
        # if not gpu_lock_ret:
        #     return utils.make_general_response(CTLResponseCode.LOCK_GPU_ERROR, "Not enough GPU available")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_count(cls) -> int:
        return 3

    @classmethod
    def subtask_invoke_2(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        pass

    @classmethod
    def subtask_invoke_1(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        pass

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        pass
