from typing import Dict, List, Optional, Tuple

from common_utils.labels import UserLabels
from controller.invoker.invoker_cmd_filter import FilterBranchInvoker
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_cmd_sampling import SamplingInvoker
from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import invoker_call, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskFusionInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if not request.in_dataset_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, 'empty in_dataset_ids')

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        subtasks_queue: List[SubTaskType] = []
        if len(request.in_dataset_ids) > 1 or request.ex_dataset_ids:
            subtasks_queue.append(cls.subtask_invoke_merge)
        if request.in_class_ids or request.ex_class_ids:
            subtasks_queue.append(cls.subtask_invoke_filter)
        if request.sampling_count or 0 < request.sampling_rate < (1.0 - 1e-9):
            subtasks_queue.append(cls.subtask_invoke_sample)
        if not subtasks_queue:  # empty ops, just copy.
            subtasks_queue.append(cls.subtask_invoke_merge)
        return [(x, 1.0 / len(subtasks_queue)) for x in subtasks_queue]

    @classmethod
    def subtask_invoke_merge(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                             assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                             subtask_workdir: str, his_task_id: Optional[str],
                             in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        """ merge """
        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=his_task_id,
            dst_dataset_id=master_task_id,
            in_dataset_ids=in_dataset_ids,
            ex_dataset_ids=request.ex_dataset_ids,
            merge_strategy=request.merge_strategy,
            work_dir=subtask_workdir,
        )
        return merge_response

    @classmethod
    def subtask_invoke_filter(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, his_task_id: Optional[str],
                              in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        if len(in_dataset_ids) != 1:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message="Invalid single in_dataset_ids {in_dataset_ids}")

        """ filter """
        filter_response = invoker_call.make_invoker_cmd_call(
            invoker=FilterBranchInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_FILTER,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=his_task_id,
            dst_dataset_id=master_task_id,
            in_dataset_ids=in_dataset_ids,
            in_class_ids=request.in_class_ids,
            ex_class_ids=request.ex_class_ids,
            work_dir=subtask_workdir,
        )
        return filter_response

    @classmethod
    def subtask_invoke_sample(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, his_task_id: Optional[str],
                              in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        if len(in_dataset_ids) != 1:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message="Invalid single in_dataset_ids {in_dataset_ids}")

        """ sampling """
        sampling_response = invoker_call.make_invoker_cmd_call(
            invoker=SamplingInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_SAMPLING,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=his_task_id,
            dst_dataset_id=master_task_id,
            in_dataset_ids=in_dataset_ids,
            sampling_count=request.sampling_count,
            sampling_rate=request.sampling_rate,
            work_dir=subtask_workdir,
        )
        return sampling_response
