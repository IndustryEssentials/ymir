import os
from typing import Dict, List, Optional, Tuple

from common_utils.labels import UserLabels
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import invoker_call, revs, utils
from controller.utils.errors import MirCtrError
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskTrainingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        train_request = request.req_create_task.training
        if not train_request.in_dataset_types:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid dataset_types")

        if not self._user_labels:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid uesr labels.")

        # store executor config in task_0 work_dir
        subtask_work_dir_0 = self.subtask_work_dir(self._work_dir, utils.sub_task_id(self._task_id, 0))
        output_config_file = self.gen_executor_config_path(subtask_work_dir_0)
        class_names = self._user_labels.main_name_for_ids(class_ids=list(request.in_class_ids))
        gpu_lock_ret = self.gen_executor_config_lock_gpus(
            req_executor_config=request.docker_image_config,
            class_names=class_names,
            task_parameters=request.task_parameters,
            output_config_file=output_config_file,
            assets_config=self._assets_config,
            preprocess=train_request.preprocess_config,
        )
        if not gpu_lock_ret:
            return utils.make_general_response(CTLResponseCode.LOCK_GPU_ERROR, "Not enough GPU available")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_merge, 0), (cls.subtask_invoke_training, 1.0)]

    @classmethod
    def subtask_invoke_merge(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                             assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                             subtask_workdir: str, his_task_id: Optional[str],
                             in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        train_request = request.req_create_task.training
        # order merged datasets by training - validation
        ordered_dataset_types = sorted(train_request.in_dataset_types, key=lambda v: v.dataset_type)
        in_dataset_ids = [
            revs.join_tvt_dataset_id(dataset_type.dataset_type, dataset_type.dataset_id)
            for dataset_type in ordered_dataset_types
        ]

        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=ordered_dataset_types[0].dataset_id,
            dst_dataset_id=master_task_id,
            in_dataset_ids=in_dataset_ids,
            merge_strategy=request.merge_strategy,
            work_dir=subtask_workdir,
        )

        return merge_response

    @classmethod
    def subtask_invoke_training(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                                assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                                subtask_workdir: str, his_task_id: Optional[str],
                                in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        if not his_task_id:
            raise MirCtrError(CTLResponseCode.INVOKER_GENERAL_ERROR, "empty previous_subtask_id in subtask_mining")

        models_upload_location = assets_config["modelsuploadlocation"]
        media_location = assets_config["assetskvlocation"]
        training_image = request.singleton_op

        tensorboard_root = assets_config["tensorboard_root"]
        tensorboard_dir = os.path.join(tensorboard_root, request.user_id, request.task_id)
        os.makedirs(tensorboard_dir, exist_ok=True)

        asset_cache_dir = os.path.join(sandbox_root, request.user_id, "asset_cache")
        os.makedirs(asset_cache_dir, exist_ok=True)

        config_file = cls.gen_executor_config_path(subtask_workdir)
        train_response = cls.training_cmd(
            repo_root=repo_root,
            label_storage_file=user_labels.storage_file,
            config_file=config_file,
            models_upload_location=models_upload_location,
            media_location=media_location,
            task_id=subtask_id,
            work_dir=subtask_workdir,
            in_dataset_id=in_dataset_ids[0],
            his_task_id=his_task_id,
            asset_cache_dir=asset_cache_dir,
            training_image=training_image,
            executant_name=request.task_id,
            tensorboard=tensorboard_dir,
            model_hash=request.model_hash,
            model_stage=request.model_stage,
        )
        return train_response

    @classmethod
    def training_cmd(
        cls,
        repo_root: str,
        label_storage_file: str,
        config_file: str,
        models_upload_location: str,
        media_location: str,
        task_id: str,
        work_dir: str,
        in_dataset_id: str,
        his_task_id: str,
        training_image: str,
        asset_cache_dir: str,
        executant_name: str,
        tensorboard: str,
        model_hash: str,
        model_stage: str,
    ) -> backend_pb2.GeneralResp:
        training_cmd = [
            utils.mir_executable(), 'train', '--root', repo_root, '--user-label-file', label_storage_file,
            '--dst-rev', f"{task_id}@{task_id}", '--model-location', models_upload_location, '--media-location',
            media_location, '-w', work_dir, '--src-revs', f"{in_dataset_id}@{his_task_id}", '--task-config-file',
            config_file, '--executor', training_image, '--executant-name', executant_name, '--tensorboard-dir',
            tensorboard, '--asset-cache-dir', asset_cache_dir
        ]
        if model_hash and model_stage:
            training_cmd.append('--model-hash')
            training_cmd.append(f"{model_hash}@{model_stage}")

        return utils.run_command(training_cmd)
