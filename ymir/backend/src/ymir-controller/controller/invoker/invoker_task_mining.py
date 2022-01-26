import os
from typing import Dict

import yaml

from common_utils.percent_log_util import LogState
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import utils, invoker_call, gpu_utils, tasks_util
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskMiningInvoker(TaskBaseInvoker):
    @classmethod
    def gen_mining_config(cls, req_mining_config: str, work_dir: str) -> str:
        mining_config = yaml.safe_load(req_mining_config)
        # when gpu_count > 0, use gpu model
        if mining_config["gpu_count"] > 0:
            gpu_ids = gpu_utils.GPUInfo().find_gpu_ids_by_config(mining_config["gpu_count"])
            if not gpu_ids:
                return gpu_ids
            else:
                mining_config["gpu_id"] = gpu_ids

        output_config = os.path.join(work_dir, "task_config.yaml")
        with open(output_config, "w") as f:
            yaml.dump(mining_config, f)

        return output_config

    @classmethod
    def task_invoke(
        cls,
        sandbox_root: str,
        repo_root: str,
        assets_config: Dict[str, str],
        working_dir: str,
        task_monitor_file: str,
        request: backend_pb2.GeneralReq,
    ) -> backend_pb2.GeneralResp:
        mining_request = request.req_create_task.mining
        if mining_request.top_k < 0:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               "invalid topk: {}".format(mining_request.top_k))
        if not request.model_hash:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid model_hash")

        if not mining_request.in_dataset_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid_data_ids")

        executor_instance = request.executor_instance
        if executor_instance != request.task_id:
            raise ValueError(f'executor_instance:{executor_instance} != task_id {request.task_id}')

        sub_task_id_1 = utils.sub_task_id(request.task_id, 1)
        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=sub_task_id_1,
            his_task_id=mining_request.in_dataset_ids[0],
            dst_task_id=request.task_id,
            in_dataset_ids=mining_request.in_dataset_ids,
            ex_dataset_ids=mining_request.ex_dataset_ids,
            merge_strategy=request.merge_strategy,
        )
        if merge_response.code != CTLResponseCode.CTR_OK:
            tasks_util.write_task_progress(monitor_file=task_monitor_file,
                                           tid=request.task_id,
                                           percent=1.0,
                                           state=LogState.ERROR,
                                           msg=merge_response.message)
            return merge_response

        sub_task_id_0 = utils.sub_task_id(request.task_id, 0)
        models_location = assets_config["modelskvlocation"]
        media_location = assets_config["assetskvlocation"]
        mining_image = request.singleton_op
        config_file = cls.gen_mining_config(request.docker_image_config, working_dir)
        if not config_file:
            msg = "Not enough GPU available"
            tasks_util.write_task_progress(task_monitor_file, request.task_id, 1, LogState.ERROR, msg)
            return utils.make_general_response(CTLResponseCode.INTERNAL_ERROR, "Not enough GPU available")

        asset_cache_dir = os.path.join(sandbox_root, request.user_id, "mining_assset_cache")
        mining_response = cls.mining_cmd(repo_root=repo_root,
                                         config_file=config_file,
                                         task_id=sub_task_id_0,
                                         work_dir=working_dir,
                                         asset_cache_dir=asset_cache_dir,
                                         model_location=models_location,
                                         media_location=media_location,
                                         top_k=mining_request.top_k,
                                         model_hash=request.model_hash,
                                         his_rev=sub_task_id_1,
                                         in_src_revs=request.task_id,
                                         executor=mining_image,
                                         executor_instance=executor_instance,
                                         generate_annotations=mining_request.generate_annotations)

        return mining_response

    @classmethod
    def mining_cmd(
        cls,
        repo_root: str,
        config_file: str,
        task_id: str,
        work_dir: str,
        model_location: str,
        media_location: str,
        top_k: int,
        model_hash: str,
        his_rev: str,
        in_src_revs: str,
        asset_cache_dir: str,
        executor: str,
        executor_instance: str,
        generate_annotations: bool,
    ) -> backend_pb2.GeneralResp:
        mining_cmd = (f"cd {repo_root} && {utils.mir_executable()} mining --dst-rev {task_id}@{task_id} "
                      f"-w {work_dir} --model-location {model_location} --media-location {media_location} "
                      f"--model-hash {model_hash} --src-revs {in_src_revs}@{his_rev} "
                      f"--cache {asset_cache_dir} --config-file {config_file} --executor {executor} "
                      f"--executor-instance {executor_instance}")
        if top_k > 0:
            mining_cmd += f" --topk {top_k}"
        if generate_annotations:
            mining_cmd += " --add-annotations"

        return utils.run_command(mining_cmd)
