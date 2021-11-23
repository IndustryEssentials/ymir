from typing import Any, List

from proto import backend_pb2


def make_cmd_request(user_id: str = None,
                     repo_id: str = None,
                     req_type: backend_pb2.RequestType = None,
                     task_id: str = None,
                     singleton_op: str = None,
                     his_task_id: str = None,
                     dst_task_id: str = None,
                     in_dataset_ids: List[str] = None,
                     ex_dataset_ids: List[str] = None,
                     in_class_ids: List[int] = None,
                     ex_class_ids: List[int] = None,
                     private_labels: List[str] = None,
                     asset_dir: str = None,
                     model_config: str = None,
                     model_hash: str = None,
                     force: bool = None,
                     commit_message: str = None,
                     req_create_task: backend_pb2.ReqCreateTask = None,
                     task_info_req: backend_pb2.ReqGetTaskInfo = None) -> backend_pb2.GeneralReq:
    request = backend_pb2.GeneralReq()
    if user_id is not None:
        request.user_id = user_id
    if repo_id is not None:
        request.repo_id = repo_id
    if req_type is not None:
        request.req_type = req_type
    if task_id is not None:
        request.task_id = task_id
    if singleton_op is not None:
        request.singleton_op = singleton_op
    if his_task_id is not None:
        request.his_task_id = his_task_id
    if dst_task_id is not None:
        request.dst_task_id = dst_task_id
    if in_dataset_ids:
        request.in_dataset_ids[:] = in_dataset_ids
    if ex_dataset_ids:
        request.ex_dataset_ids[:] = ex_dataset_ids
    if in_class_ids:
        request.in_class_ids[:] = in_class_ids
    if ex_class_ids:
        request.ex_class_ids[:] = ex_class_ids
    if private_labels:
        request.private_labels[:] = private_labels
    if force is not None:
        request.force = force
    if commit_message is not None:
        request.commit_message = commit_message
    if asset_dir is not None:
        request.asset_dir = asset_dir
    if model_config is not None:
        request.model_config = model_config
    if model_hash is not None:
        request.model_hash = model_hash
    if req_create_task is not None:
        request.req_create_task.CopyFrom(req_create_task)
    if task_info_req is not None:
        request.req_get_task_info.CopyFrom(task_info_req)
    return request


def make_invoker_cmd_call(invoker: Any,
                          sandbox_root: str = None,
                          assets_config: dict = None,
                          req_type: backend_pb2.RequestType = None,
                          user_id: str = None,
                          repo_id: str = None,
                          task_id: str = None,
                          singleton_op: str = None,
                          his_task_id: str = None,
                          dst_task_id: str = None,
                          in_dataset_ids: List[str] = None,
                          ex_dataset_ids: List[str] = None,
                          in_class_ids: List[int] = None,
                          ex_class_ids: List[int] = None,
                          force: bool = None,
                          commit_message: str = None,
                          req_create_task: backend_pb2.ReqCreateTask = None,
                          task_info_req: backend_pb2.ReqGetTaskInfo = None,
                          async_mode: bool = False) -> backend_pb2.GeneralReq:
    request = make_cmd_request(req_type=req_type,
                               user_id=user_id,
                               repo_id=repo_id,
                               task_id=task_id,
                               singleton_op=singleton_op,
                               his_task_id=his_task_id,
                               dst_task_id=dst_task_id,
                               in_dataset_ids=in_dataset_ids,
                               ex_dataset_ids=ex_dataset_ids,
                               in_class_ids=in_class_ids,
                               ex_class_ids=ex_class_ids,
                               force=force,
                               commit_message=commit_message,
                               req_create_task=req_create_task,
                               task_info_req=task_info_req)
    invoker = invoker(sandbox_root=sandbox_root, request=request, assets_config=assets_config, async_mode=async_mode)
    return invoker.server_invoke()
