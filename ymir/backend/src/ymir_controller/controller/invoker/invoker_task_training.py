import os
from typing import Dict, List

from common_utils.labels import UserLabels
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import invoker_call, revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskTrainingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        train_request = request.req_create_task.training
        if not train_request.in_dataset_types:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid dataset_types")

        # store executor config in task_0 work_dir
        subtask_work_dir_0 = self.subtask_work_dir(self._work_dir, utils.sub_task_id(self._task_id, 0))
        output_config_file = self.gen_executor_config_path(subtask_work_dir_0)
        class_names = self._user_labels.get_main_names(class_ids=list(train_request.in_class_ids))
        gpu_lock_ret = self.gen_executor_config_lock_gpus(
            req_executor_config=request.docker_image_config,
            class_names=class_names,
            task_parameters=request.task_parameters,
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
        train_request = request.req_create_task.training
        in_dataset_ids = [
            revs.join_tvt_dataset_id(dataset_type.dataset_type, dataset_type.dataset_id)
            for dataset_type in train_request.in_dataset_types
        ]

        merge_response = invoker_call.make_invoker_cmd_call(
            invoker=MergeInvoker,
            sandbox_root=sandbox_root,
            req_type=backend_pb2.CMD_MERGE,
            user_id=request.user_id,
            repo_id=request.repo_id,
            task_id=subtask_id,
            his_task_id=train_request.in_dataset_types[0].dataset_id,
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
        models_upload_location = assets_config["modelsuploadlocation"]
        media_location = assets_config["assetskvlocation"]
        training_image = request.singleton_op

        tensorboard_root = assets_config['tensorboard_root']
        tensorboard_dir = os.path.join(tensorboard_root, request.user_id, request.task_id)
        os.makedirs(tensorboard_dir, exist_ok=True)

        config_file = cls.gen_executor_config_path(subtask_workdir)
        asset_cache_dir = os.path.join(sandbox_root, request.user_id, "training_assset_cache")
        executant_name = request.task_id
        train_response = cls.training_cmd(
            repo_root=repo_root,
            config_file=config_file,
            models_upload_location=models_upload_location,
            media_location=media_location,
            task_id=subtask_id,
            work_dir=subtask_workdir,
            in_dataset_id=request.task_id,
            his_task_id=previous_subtask_id,
            asset_cache_dir=asset_cache_dir,
            training_image=training_image,
            executant_name=executant_name,
            tensorboard=tensorboard_dir,
            model_hash=request.model_hash,
        )
        return train_response

    @classmethod
    def training_cmd(
        cls,
        repo_root: str,
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
    ) -> backend_pb2.GeneralResp:
        training_cmd = [
            utils.mir_executable(), 'train', '--root', repo_root, '--dst-rev', f"{task_id}@{task_id}",
            '--model-location', models_upload_location, '--media-location', media_location, '-w', work_dir,
            '--src-revs', f"{in_dataset_id}@{his_task_id}", '--task-config-file', config_file, '--executor',
            training_image, '--executant-name', executant_name, '--tensorboard-dir', tensorboard,
            '--asset-cache-dir', asset_cache_dir
        ]
        if model_hash:
            training_cmd.append('--model-hash')
            training_cmd.append(model_hash)

        return utils.run_command(training_cmd)
