import logging
from typing import Dict, List
from common_utils.labels import UserLabels

from controller.invoker.invoker_cmd_filter import FilterBranchInvoker
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import invoker_call, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskFilterInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        filter_request = request.req_create_task.filter
        logging.info(f"filter_request: {filter_request}")
        if not filter_request.in_dataset_ids:
            return utils.make_general_response(
                code=CTLResponseCode.ARG_VALIDATION_FAILED,
                message="invalid_data_ids",
            )

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [0.5, 0.5]

    @classmethod
    def subtask_invoke_1(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        filter_request = request.req_create_task.filter
        in_dataset_ids = list(filter_request.in_dataset_ids)
        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=in_dataset_ids[0],
            dst_dataset_id=request.task_id,
            in_dataset_ids=in_dataset_ids,
            merge_strategy=request.merge_strategy,
            work_dir=subtask_workdir,
        )
        return merge_response

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        filter_request = request.req_create_task.filter

        filter_response = invoker_call.make_invoker_cmd_call(
            invoker=FilterBranchInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_FILTER,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=previous_subtask_id,
            dst_dataset_id=request.task_id,
            in_dataset_ids=[request.task_id],
            in_class_ids=filter_request.in_class_ids,
            ex_class_ids=filter_request.ex_class_ids,
            work_dir=subtask_workdir,
        )

        return filter_response
