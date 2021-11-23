import os
from typing import Dict

import yaml

from controller.invoker.invoker_cmd_merge import MergeInvoker
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import code, utils, invoker_call
from proto import backend_pb2


class TaskMiningInvoker(TaskBaseInvoker):
    @classmethod
    def gen_mining_config(cls, req_mining_config: str, work_dir: str) -> str:
        training_config = yaml.safe_load(req_mining_config)
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
        mining_request = request.req_create_task.mining
        if mining_request.top_k < 0:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ,
                                               "invalid topk: {}".format(mining_request.top_k))
        if not mining_request.model_hash:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, "invalid model_hash")

        if not mining_request.in_dataset_ids:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, "invalid_data_ids")

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
        )
        if merge_response.code != code.ResCode.CTR_OK:
            return merge_response

        sub_task_id_0 = utils.sub_task_id(request.task_id, 0)
        models_location = assets_config["modelskvlocation"]
        media_location = assets_config["assetskvlocation"]
        mining_image = assets_config["mining_image"]
        config_file = cls.gen_mining_config(mining_request.mining_config, working_dir)
        asset_cache_dir = os.path.join(sandbox_root, request.user_id, "mining_assset_cache")
        mining_response = cls.mining_cmd(repo_root=repo_root,
                                         config_file=config_file,
                                         task_id=sub_task_id_0,
                                         work_dir=working_dir,
                                         asset_cache_dir=asset_cache_dir,
                                         model_location=models_location,
                                         media_location=media_location,
                                         top_k=mining_request.top_k,
                                         model_hash=mining_request.model_hash,
                                         his_rev=sub_task_id_1,
                                         in_src_revs=request.task_id,
                                         executor=mining_image)

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
    ) -> backend_pb2.GeneralResp:
        mining_cmd = (f"cd {repo_root} && {utils.mir_executable()} mining --dst-rev {task_id}@{task_id} "
                      f"-w {work_dir} --model-location {model_location} --media-location {media_location} "
                      f"--topk {top_k} --model-hash {model_hash} --src-revs {in_src_revs}@{his_rev} "
                      f"--cache {asset_cache_dir} --config-file {config_file} --executor {executor}")

        return utils.run_command(mining_cmd)

    def _repr(self) -> str:
        mining_request = self._request.req_create_task.mining
        repr = (f"task_mining: user: {self._request.user_id},repo: {self._request.repo_id} task_id: {self._task_id} "
                f"model_hash: {mining_request.model_hash} top_k: {mining_request.top_k} in_dataset_ids: "
                f"{mining_request.in_dataset_ids} ex_dataset_ids: {mining_request.ex_dataset_ids} cached")

        return repr
