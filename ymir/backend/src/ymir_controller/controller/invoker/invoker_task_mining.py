import logging
import os
from typing import Dict, List
from common_utils.labels import UserLabels

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
            req_executor_config=request.docker_image_config,
            task_parameters=request.task_parameters,
            class_names=[],
            output_config_file=output_config_file,
        )
        if not gpu_lock_ret:
            return utils.make_general_response(CTLResponseCode.LOCK_GPU_ERROR, "Not enough GPU available")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0, 0.0]

    @classmethod
    def subtask_invoke_1(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        mining_request = request.req_create_task.mining
        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=mining_request.in_dataset_ids[0],
            dst_dataset_id=request.task_id,
            in_dataset_ids=mining_request.in_dataset_ids,
            ex_dataset_ids=mining_request.ex_dataset_ids,
            merge_strategy=request.merge_strategy,
            work_dir=subtask_workdir,
        )
        return merge_response

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        mining_request = request.req_create_task.mining
        executant_name = request.task_id
        models_location = assets_config["modelskvlocation"]
        media_location = assets_config["assetskvlocation"]
        mining_image = request.singleton_op

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
                                         in_dataset_id=request.task_id,
                                         his_task_id=previous_subtask_id,
                                         executor=mining_image,
                                         executant_name=executant_name,
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
        in_dataset_id: str,
        his_task_id: str,
        asset_cache_dir: str,
        executor: str,
        executant_name: str,
        generate_annotations: bool,
    ) -> backend_pb2.GeneralResp:
        mining_cmd = [
            utils.mir_executable(), 'mining', '--root', repo_root, '--dst-rev', f"{task_id}@{task_id}", '-w', work_dir,
            '--model-location', model_location, '--media-location', media_location, '--model-hash', model_hash,
            '--src-revs', f"{in_dataset_id}@{his_task_id}", '--asset-cache-dir', asset_cache_dir, '--task-config-file',
            config_file, '--executor', executor, '--executant-name', executant_name
        ]
        if top_k > 0:
            mining_cmd.append('--topk')
            mining_cmd.append(str(top_k))
        if generate_annotations:
            mining_cmd.append('--add-annotations')

        return utils.run_command(mining_cmd)
