from distutils.util import strtobool
import logging
from typing import Any, Dict, List, Optional

import requests
import yaml

from controller.config import common_task as common_task_config
from controller.utils import errors, gpu_utils
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb


def register_monitor_log(task_id: str,
                         log_path_weights: Dict[str, float],
                         description: str = None) -> None:
    resp = requests.post(
        url=f"{common_task_config.MONITOR_URL}/api/v1/tasks",
        json=dict(task_id=task_id, log_path_weights=log_path_weights, description=description),
        timeout=5,
    )

    if resp.status_code != 200:
        raise errors.MirCtrError(CTLResponseCode.REG_LOG_MONITOR_ERROR, f"reg to monitor service error: {resp.text}")


def gen_executor_config_find_gpus(req_executor_config: str,
                                  class_names: List,
                                  output_config_file: str,
                                  object_type: "mir_cmd_pb.ObjectType.V",
                                  assets_config: Dict = {},
                                  preprocess: Optional[str] = None,
                                  lock_gpu: bool = True) -> bool:
    executor_config = yaml.safe_load(req_executor_config)
    preprocess_config = yaml.safe_load(preprocess) if preprocess else None
    task_context: Dict[str, Any] = {}

    if class_names:
        executor_config["class_names"] = class_names

    if preprocess_config:
        task_context["preprocess"] = preprocess_config

    task_context['server_runtime'] = assets_config['server_runtime']
    task_context["object_type"] = object_type

    gpu_count = executor_config.get("gpu_count", 0)
    executor_config["gpu_id"] = ",".join([str(i) for i in range(gpu_count)])
    executor_config["object_type"] = object_type

    # Openpai enabled
    if strtobool(str(executor_config.get("openpai_enable", "False"))):
        openpai_host = assets_config.get("openpai_host", None)
        openpai_token = assets_config.get("openpai_token", None)
        openpai_storage = assets_config.get("openpai_storage", None)
        openpai_user = assets_config.get("openpai_user", "")
        openpai_cluster = assets_config.get("openpai_cluster")
        openpai_gputype = assets_config.get("openpai_gputype")
        logging.info(
            f"OpenPAI host: {openpai_host}, token: {openpai_token}, "
            f"storage: {openpai_storage}, user: {openpai_user}",
            f"cluster: {openpai_cluster}, gpu_type: {openpai_gputype}")

        if not (openpai_host and openpai_token and openpai_storage and openpai_user):
            raise errors.MirCtrError(
                CTLResponseCode.INVOKER_INVALID_ARGS,
                "openpai enabled with invalid host, token, storage or user",
            )
        task_context["openpai_enable"] = True
        task_context["openpai_host"] = openpai_host
        task_context["openpai_token"] = openpai_token
        task_context["openpai_storage"] = openpai_storage
        task_context["openpai_user"] = openpai_user
        task_context["openpai_cluster"] = openpai_cluster
        task_context["openpai_gputype"] = openpai_gputype

        task_context["available_gpu_id"] = executor_config["gpu_id"]
    else:
        # lock local gpus.
        gpu_ids = gpu_utils.GPUInfo().find_gpu_ids_by_config(gpu_count, lock_gpu=lock_gpu)
        if gpu_ids is None:
            return False
        task_context["available_gpu_id"] = gpu_ids

    with open(output_config_file, "w") as f:
        yaml.safe_dump(dict(
            executor_config=executor_config,
            task_context=task_context,
        ), f, allow_unicode=True)

    return True
