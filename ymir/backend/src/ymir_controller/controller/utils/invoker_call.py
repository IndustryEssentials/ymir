from typing import Any, List

from proto import backend_pb2


def make_cmd_request(user_id: str = None,
                     repo_id: str = None,
                     req_type: backend_pb2.RequestType = None,
                     task_id: str = None,
                     singleton_op: str = None,
                     his_task_id: str = None,
                     dst_dataset_id: str = None,
                     in_dataset_ids: List[str] = None,
                     ex_dataset_ids: List[str] = None,
                     in_class_ids: List[int] = None,
                     ex_class_ids: List[int] = None,
                     label_collection: backend_pb2.LabelCollection = None,
                     asset_dir: str = None,
                     model_config: str = None,
                     model_hash: str = None,
                     force: bool = None,
                     commit_message: str = None,
                     executant_name: str = None,
                     merge_strategy: int = None,
                     req_create_task: backend_pb2.ReqCreateTask = None,
                     docker_image_config: str = None,
                     terminated_task_type: str = None,
                     sampling_count: int = None,
                     sampling_rate: float = None,
                     task_parameters: str = None,
                     evaluate_config: backend_pb2.EvaluateConfig = None) -> backend_pb2.GeneralReq:
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
    if dst_dataset_id is not None:
        request.dst_dataset_id = dst_dataset_id
    if in_dataset_ids:
        request.in_dataset_ids[:] = in_dataset_ids
    if ex_dataset_ids:
        request.ex_dataset_ids[:] = ex_dataset_ids
    if in_class_ids:
        request.in_class_ids[:] = in_class_ids
    if ex_class_ids:
        request.ex_class_ids[:] = ex_class_ids
    if label_collection:
        request.label_collection.CopyFrom(label_collection)
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
    if executant_name is not None:
        request.executant_name = executant_name
    if merge_strategy is not None:
        request.merge_strategy = merge_strategy
    if docker_image_config is not None:
        request.docker_image_config = docker_image_config
    if terminated_task_type is not None:
        request.terminated_task_type = terminated_task_type
    if sampling_count:
        request.sampling_count = sampling_count
    if sampling_rate:
        request.sampling_rate = sampling_rate
    if task_parameters:
        request.task_parameters = task_parameters
    if evaluate_config:
        request.evaluate_config.CopyFrom(evaluate_config)
    return request


def make_invoker_cmd_call(invoker: Any,
                          sandbox_root: str = None,
                          assets_config: dict = None,
                          req_type: backend_pb2.RequestType = None,
                          user_id: str = None,
                          repo_id: str = None,
                          task_id: str = None,
                          executant_name: str = None,
                          singleton_op: str = None,
                          his_task_id: str = None,
                          dst_dataset_id: str = None,
                          in_dataset_ids: List[str] = None,
                          ex_dataset_ids: List[str] = None,
                          in_class_ids: List[int] = None,
                          ex_class_ids: List[int] = None,
                          label_collection: backend_pb2.LabelCollection = None,
                          force: bool = None,
                          commit_message: str = None,
                          req_create_task: backend_pb2.ReqCreateTask = None,
                          async_mode: bool = False,
                          merge_strategy: int = None,
                          model_hash: str = None,
                          docker_image_config: str = None,
                          terminated_task_type: str = None,
                          sampling_count: int = None,
                          sampling_rate: float = None,
                          work_dir: str = '',
                          evaluate_config: backend_pb2.EvaluateConfig = None) -> backend_pb2.GeneralReq:
    request = make_cmd_request(req_type=req_type,
                               user_id=user_id,
                               repo_id=repo_id,
                               task_id=task_id,
                               singleton_op=singleton_op,
                               his_task_id=his_task_id,
                               dst_dataset_id=dst_dataset_id,
                               in_dataset_ids=in_dataset_ids,
                               ex_dataset_ids=ex_dataset_ids,
                               in_class_ids=in_class_ids,
                               ex_class_ids=ex_class_ids,
                               label_collection=label_collection,
                               force=force,
                               commit_message=commit_message,
                               req_create_task=req_create_task,
                               executant_name=executant_name,
                               merge_strategy=merge_strategy,
                               model_hash=model_hash,
                               docker_image_config=docker_image_config,
                               terminated_task_type=terminated_task_type,
                               sampling_count=sampling_count,
                               sampling_rate=sampling_rate,
                               evaluate_config=evaluate_config)
    invoker = invoker(sandbox_root=sandbox_root,
                      request=request,
                      assets_config=assets_config,
                      async_mode=async_mode,
                      work_dir=work_dir)
    return invoker.server_invoke()
