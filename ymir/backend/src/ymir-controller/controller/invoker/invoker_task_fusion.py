from typing import Dict

from controller.invoker.invoker_cmd_filter import FilterBranchInvoker
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_cmd_sampling import SamplingInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import invoker_call, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskFusionInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if not request.req_create_task.fusion.in_dataset_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, 'empty in_dataset_ids')

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_count(cls) -> int:
        return 3

    @classmethod
    def subtask_invoke_2(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        """ merge """
        fusion_req = request.req_create_task.fusion
        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            dst_task_id=subtask_id,
            his_task_id=fusion_req.in_dataset_ids[0],
            in_dataset_ids=fusion_req.in_dataset_ids,
            ex_dataset_ids=fusion_req.ex_dataset_ids,
            merge_strategy=fusion_req.merge_strategy,
            work_dir=subtask_workdir,
        )
        return merge_response

    @classmethod
    def subtask_invoke_1(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        """ filter """
        fusion_req = request.req_create_task.fusion
        filter_response = invoker_call.make_invoker_cmd_call(
            invoker=FilterBranchInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_FILTER,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            dst_task_id=subtask_id,
            his_task_id=subtask_id_dict[2],
            in_dataset_ids=[subtask_id_dict[2]],
            in_class_ids=fusion_req.in_class_ids,
            ex_class_ids=fusion_req.ex_class_ids,
            work_dir=subtask_workdir,
        )
        return filter_response

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        """ sampling """
        fusion_req = request.req_create_task.fusion
        sampling_response = invoker_call.make_invoker_cmd_call(
            invoker=SamplingInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_SAMPLING,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=request.task_id,
            in_dataset_ids=[subtask_id_dict[1]],
            count=fusion_req.count,
            rate=fusion_req.rate,
            work_dir=subtask_workdir,
        )
        return sampling_response
