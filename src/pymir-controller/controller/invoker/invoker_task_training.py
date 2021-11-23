import os
import time
from typing import List, Dict, Set

import yaml

from controller.config import GPU_LOCKING_SET
from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import code, utils, invoker_call, revs, gpu_utils, labels
from controller.utils.redis import rds
from proto import backend_pb2


class TaskTrainingInvoker(TaskBaseInvoker):
    @classmethod
    def get_locked_gpus(cls) -> Set:
        # lock gpu about 30 minutes for loading
        cut_off_time = time.time() - 60 * 30
        rds.zremrangebyscore(GPU_LOCKING_SET, cut_off_time)
        locked_gpus = rds.zrange(GPU_LOCKING_SET)

        return set(locked_gpus)

    @classmethod
    def add_locked_gpus(cls, gpus: List[str]) -> None:
        gpu_mapping = {gpu: time.time() for gpu in gpus}
        rds.zadd(GPU_LOCKING_SET, gpu_mapping)

    @classmethod
    def get_available_gpus(cls) -> List:
        runtime_free_gpus = gpu_utils.get_free_gpus()
        locked_gpus = cls.get_locked_gpus()
        ava_gpus = runtime_free_gpus - locked_gpus

        return list(ava_gpus)

    @classmethod
    def find_gpu_ids(cls, training_config: Dict) -> str:
        gpu_count = training_config.pop("gpu_count", None)
        if gpu_count is None:
            gpu_count = len(training_config["gpu_id"].split(","))

        free_gpus = cls.get_available_gpus()
        if len(free_gpus) < gpu_count:
            return ''

        gpus = free_gpus[0:gpu_count]
        cls.add_locked_gpus(gpus)

        return ",".join(gpus)

    @classmethod
    def gen_training_config(cls, repo_root: str, req_training_config: str, in_class_ids: List, work_dir: str) -> str:
        training_config = yaml.safe_load(req_training_config)
        label_handler = labels.LabelFileHandler(repo_root)
        training_config["class_names"] = label_handler.get_main_labels_by_ids(in_class_ids)

        gpu_ids = cls.find_gpu_ids(training_config)
        if not gpu_ids:
            return gpu_ids
        else:
            training_config["gpu_id"] = gpu_ids
        output_config = os.path.join(work_dir, "task_config.yaml")
        with open(output_config, "w") as f:
            yaml.dump(training_config, f)

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
        train_request = request.req_create_task.training
        if not train_request.in_dataset_types:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, "invalid dataset_types")

        sub_task_id_1 = utils.sub_task_id(request.task_id, 1)
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
            task_id=sub_task_id_1,
            his_task_id=train_request.in_dataset_types[0].dataset_id,
            dst_task_id=request.task_id,
            in_dataset_ids=in_dataset_ids,
        )
        if merge_response.code != code.ResCode.CTR_OK:
            return merge_response

        sub_task_id = utils.sub_task_id(request.task_id, 0)
        models_upload_location = assets_config["modelsuploadlocation"]
        media_location = assets_config["assetskvlocation"]
        training_image = assets_config["training_image"]
        config_file = cls.gen_training_config(repo_root, train_request.training_config, train_request.in_class_ids, working_dir)
        if not config_file:
            return utils.make_general_response(code.ResCode.CTR_ERROR_UNKNOWN, "Not enough GPU available")

        train_response = cls.training_cmd(
            repo_root=repo_root,
            config_file=config_file,
            models_upload_location=models_upload_location,
            media_location=media_location,
            task_id=sub_task_id,
            work_dir=working_dir,
            his_rev=sub_task_id_1,
            in_src_revs=request.task_id,
            training_image=training_image,
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
    ) -> backend_pb2.GeneralResp:
        training_cmd = (f"cd {repo_root} && {utils.mir_executable()} train --dst-rev {task_id}@{task_id} "
                        f"--model-location {models_upload_location} --media-location {media_location} -w {work_dir} "
                        f"--src-revs {in_src_revs}@{his_rev} --config-file {config_file} --executor {training_image}")
        return utils.run_command(training_cmd)

    def _repr(self) -> str:
        train_request = self._request.req_create_task.training
        in_dataset_ids = [
            revs.join_tvt_dataset_id(dataset_type.dataset_type, dataset_type.dataset_id)
            for dataset_type in train_request.in_dataset_types
        ]

        repr = (f"task_training: user: {self._request.user_id}, repo: {self._request.repo_id} task_id: {self._task_id} "
                f"in_dataset_types: {in_dataset_ids} in_class_ids: {train_request.in_class_ids}")

        return repr
