import logging
import os
from typing import Dict

from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import utils, invoker_call
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskMiningInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        mining_request = request.req_create_task.mining
        logging.info(f"mining_request: {mining_request}")
        if mining_request.top_k < 0:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               "invalid topk: {}".format(mining_request.top_k))
        if not request.model_hash:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid model_hash")

        if not mining_request.in_dataset_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid_data_ids")

        # store executor config in task_0 work_dir
        subtask_work_dir_0 = self.subtask_work_dir(self._work_dir, utils.sub_task_id(self._task_id, 0))
        output_config_file = self.gen_executor_config_path(subtask_work_dir_0)
        gpu_lock_ret = self.gen_executor_config_lock_gpus(
            repo_root=self._repo_root,
            req_executor_config=request.docker_image_config,
            in_class_ids=[],
            output_config_file=output_config_file,
        )
        if not gpu_lock_ret:
            return utils.make_general_response(CTLResponseCode.LOCK_GPU_ERROR, "Not enough GPU available")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_count(cls) -> int:
        return 2

    @classmethod
    def subtask_invoke_1(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        mining_request = request.req_create_task.mining
        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=mining_request.in_dataset_ids[0],
            dst_task_id=request.task_id,
            in_dataset_ids=mining_request.in_dataset_ids,
            ex_dataset_ids=mining_request.ex_dataset_ids,
            merge_strategy=request.merge_strategy,
            work_dir=subtask_workdir,
        )
        return merge_response

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        mining_request = request.req_create_task.mining
        executor_instance = request.task_id
        models_location = assets_config["modelskvlocation"]
        media_location = assets_config["assetskvlocation"]
        mining_image = request.singleton_op

        previous_subtask_idx = 1
        config_file = cls.gen_executor_config_path(subtask_workdir)
        asset_cache_dir = os.path.join(sandbox_root, request.user_id, "mining_assset_cache")
        mining_response = cls.mining_cmd(repo_root=repo_root,
                                         config_file=config_file,
                                         task_id=subtask_id,
                                         work_dir=subtask_workdir,
                                         asset_cache_dir=asset_cache_dir,
                                         model_location=models_location,
                                         media_location=media_location,
                                         top_k=mining_request.top_k,
                                         model_hash=request.model_hash,
                                         his_rev=subtask_id_dict[previous_subtask_idx],
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
