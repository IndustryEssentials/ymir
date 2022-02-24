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
                     executor_instance: str = None,
                     merge_strategy: int = None,
                     req_create_task: backend_pb2.ReqCreateTask = None,
                     docker_image_config: str = None,
                     terminated_task_type: str = None) -> backend_pb2.GeneralReq:
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
    if executor_instance is not None:
        request.executor_instance = executor_instance
    if merge_strategy is not None:
        request.merge_strategy = merge_strategy
    if docker_image_config is not None:
        request.docker_image_config = docker_image_config
    if terminated_task_type is not None:
        request.terminated_task_type = terminated_task_type
    return request


def make_invoker_cmd_call(invoker: Any,
                          sandbox_root: str = None,
                          assets_config: dict = None,
                          req_type: backend_pb2.RequestType = None,
                          user_id: str = None,
                          repo_id: str = None,
                          task_id: str = None,
                          executor_instance: str = None,
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
                          async_mode: bool = False,
                          merge_strategy: int = None,
                          model_hash: str = None,
                          docker_image_config: str = None,
                          terminated_task_type: str = None,
                          work_dir: str = '') -> backend_pb2.GeneralReq:
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
                               executor_instance=executor_instance,
                               merge_strategy=merge_strategy,
                               model_hash=model_hash,
                               docker_image_config=docker_image_config,
                               terminated_task_type=terminated_task_type)
    invoker = invoker(sandbox_root=sandbox_root,
                      request=request,
                      assets_config=assets_config,
                      async_mode=async_mode,
                      work_dir=work_dir)
    return invoker.server_invoke()
