import os
from typing import Dict, List, Optional, Tuple

from common_utils.labels import UserLabels
from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskMiningInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if not request.in_dataset_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid_data_ids")

        mining_request = request.req_create_task.mining
        if mining_request.top_k < 0:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               f"invalid topk: {mining_request.top_k}")
        if not request.model_hash or not request.model_stage:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid model_hash")

        # store executor config in task_0 work_dir
        subtask_work_dir_0 = self.subtask_work_dir(self._work_dir, utils.sub_task_id(self._task_id, 0))
        output_config_file = self.gen_executor_config_path(subtask_work_dir_0)
        gpu_lock_ret = self.gen_executor_config_lock_gpus(
            req_executor_config=request.docker_image_config,
            task_parameters=request.task_parameters,
            class_names=[],
            output_config_file=output_config_file,
            assets_config=self._assets_config,
        )
        if not gpu_lock_ret:
            return utils.make_general_response(CTLResponseCode.LOCK_GPU_ERROR, "Not enough GPU available")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_mining, 1.0)]

    @classmethod
    def subtask_invoke_mining(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, his_task_id: Optional[str],
                              in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        mining_request = request.req_create_task.mining
        executant_name = request.task_id
        models_location = assets_config["modelskvlocation"]
        media_location = assets_config["assetskvlocation"]
        mining_image = request.singleton_op

        config_file = cls.gen_executor_config_path(subtask_workdir)
        asset_cache_dir = os.path.join(sandbox_root, request.user_id, "asset_cache")
        mining_response = cls.mining_cmd(repo_root=repo_root,
                                         label_storage_file=user_labels.storage_file,
                                         config_file=config_file,
                                         task_id=subtask_id,
                                         work_dir=subtask_workdir,
                                         asset_cache_dir=asset_cache_dir,
                                         model_location=models_location,
                                         media_location=media_location,
                                         top_k=mining_request.top_k,
                                         model_hash=request.model_hash,
                                         model_stage=request.model_stage,
                                         in_dataset_ids=request.in_dataset_ids,
                                         ex_dataset_ids=request.ex_dataset_ids,
                                         merge_strategy=request.merge_strategy,
                                         executor=mining_image,
                                         executant_name=executant_name,
                                         generate_annotations=mining_request.generate_annotations)

        return mining_response

    @classmethod
    def mining_cmd(
        cls,
        repo_root: str,
        label_storage_file: str,
        config_file: str,
        task_id: str,
        work_dir: str,
        model_location: str,
        media_location: str,
        top_k: int,
        model_hash: str,
        model_stage: str,
        in_dataset_ids: List[str],
        ex_dataset_ids: List[str],
        merge_strategy: backend_pb2.MergeStrategy,
        asset_cache_dir: str,
        executor: str,
        executant_name: str,
        generate_annotations: bool,
    ) -> backend_pb2.GeneralResp:
        mining_cmd = [
            utils.mir_executable(), 'mining', '--root', repo_root, '--user-label-file', label_storage_file, '--dst-rev',
            f"{task_id}@{task_id}", '-w', work_dir, '--model-location', model_location, '--media-location',
            media_location, '--model-hash', f"{model_hash}@{model_stage}", '--src-revs',
            revs.build_src_revs(in_dataset_ids)
        ]
        if ex_dataset_ids:
            mining_cmd.extend(['--ex-src-revs', revs.build_src_revs(ex_dataset_ids)])
        mining_cmd.extend([
            '-s', backend_pb2.MergeStrategy.Name(merge_strategy).lower(), '--asset-cache-dir', asset_cache_dir,
            '--task-config-file', config_file, '--executor', executor, '--executant-name', executant_name
        ])
        if top_k > 0:
            mining_cmd.extend(['--topk', str(top_k)])
        if generate_annotations:
            mining_cmd.append('--add-prediction')

        return utils.run_command(mining_cmd)
