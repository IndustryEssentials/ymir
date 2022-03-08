import os
from typing import Dict, List

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
        gpu_lock_ret = self.gen_executor_config_lock_gpus(
            repo_root=self._repo_root,
            req_executor_config=request.docker_image_config,
            in_class_ids=train_request.in_class_ids,
            output_config_file=output_config_file,
        )
        if not gpu_lock_ret:
            return utils.make_general_response(CTLResponseCode.LOCK_GPU_ERROR, "Not enough GPU available")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [0.99, 0.01]

    @classmethod
    def subtask_invoke_1(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
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
                         subtask_id_dict: Dict[int, str]) -> backend_pb2.GeneralResp:
        models_upload_location = assets_config["modelsuploadlocation"]
        media_location = assets_config["assetskvlocation"]
        training_image = request.singleton_op

        tensorboard_root = assets_config['tensorboard_root']
        tensorboard_dir = os.path.join(tensorboard_root, request.user_id, request.task_id)
        os.makedirs(tensorboard_dir, exist_ok=True)

        previous_subtask_idx = 1
        config_file = cls.gen_executor_config_path(subtask_workdir)
        executor_instance = request.task_id
        train_response = cls.training_cmd(
            repo_root=repo_root,
            config_file=config_file,
            models_upload_location=models_upload_location,
            media_location=media_location,
            task_id=subtask_id,
            work_dir=subtask_workdir,
            his_rev=subtask_id_dict[previous_subtask_idx],
            in_src_revs=request.task_id,
            training_image=training_image,
            executor_instance=executor_instance,
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
        his_rev: str,
        in_src_revs: str,
        training_image: str,
        executor_instance: str,
        tensorboard: str,
        model_hash: str,
    ) -> backend_pb2.GeneralResp:
        training_cmd = [
            utils.mir_executable(), 'train', '--root', repo_root,
            '--dst-rev', f"{task_id}@{task_id}", '--model-location',
            models_upload_location, '--media-location', media_location, '-w', work_dir, '--src-revs',
            f"{in_src_revs}@{his_rev}", '--config-file', config_file, '--executor', training_image,
            '--executor-instance', executor_instance, '--tensorboard', tensorboard
        ]
        if model_hash:
            training_cmd.append('--model-hash')
            training_cmd.append(model_hash)

        return utils.run_command(training_cmd)
