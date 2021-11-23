from controller.invoker.invoker_cmd_filter import FilterBranchInvoker
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker, write_done_progress
from controller.utils import code, invoker_call, utils
from proto import backend_pb2


class TaskFilterInvoker(TaskBaseInvoker):
    @classmethod
    @write_done_progress
    def task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: str, working_dir: str,
                    task_monitor_file: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        # Use sub_task_id 0 as end of task.
        filter_request = request.req_create_task.filter

        if not filter_request.in_dataset_ids:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, "invalid_data_ids")

        in_dataset_ids = list(filter_request.in_dataset_ids)
        sub_task_id_1 = utils.sub_task_id(request.task_id, 1)
        merge_response = invoker_call.make_invoker_cmd_call(invoker=MergeInvoker,
                                                            sandbox_root=sandbox_root,
                                                            req_type=backend_pb2.CMD_MERGE,
                                                            user_id=request.user_id,
                                                            repo_id=request.repo_id,
                                                            task_id=sub_task_id_1,
                                                            his_task_id=in_dataset_ids[0],
                                                            dst_task_id=request.task_id,
                                                            in_dataset_ids=in_dataset_ids)
        if merge_response.code != code.ResCode.CTR_OK:
            return merge_response

        sub_task_id_0 = utils.sub_task_id(request.task_id, 0)
        filter_response = invoker_call.make_invoker_cmd_call(invoker=FilterBranchInvoker,
                                                             sandbox_root=sandbox_root,
                                                             req_type=backend_pb2.CMD_FILTER,
                                                             user_id=request.user_id,
                                                             repo_id=request.repo_id,
                                                             task_id=sub_task_id_0,
                                                             his_task_id=sub_task_id_1,
                                                             dst_task_id=request.task_id,
                                                             in_dataset_ids=[request.task_id],
                                                             in_class_ids=filter_request.in_class_ids,
                                                             ex_class_ids=filter_request.ex_class_ids)

        return filter_response

    def _repr(self) -> str:
        filter_request = self._request.req_create_task.filter
        return ("task_filter: user: {}, repo: {} task_id: {} in_dataset_ids: {} "
                "in_class_ids: {} ex_class_ids: {}".format(self._request.user_id, self._request.repo_id, self._task_id,
                                                           filter_request.in_dataset_ids, filter_request.in_class_ids,
                                                           filter_request.ex_class_ids))
