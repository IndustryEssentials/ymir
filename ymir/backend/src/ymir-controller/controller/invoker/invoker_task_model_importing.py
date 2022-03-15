from ctypes import util
import logging
import os
from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class InvokerTaskModelImporting(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        model_importing_request = request.req_create_task.model_importing
        logging.info(f"model_importing_request: {model_importing_request}")
        model_package_path = model_importing_request.model_package_path
        if not os.path.isfile(model_package_path):
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"file not exists: {model_package_path}")

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0]

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str) -> backend_pb2.GeneralResp:
        # paths
        model_location = assets_config["modelsuploadlocation"]
        model_importing_request = request.req_create_task.model_importing
        model_package_path = model_importing_request.model_package_path

        model_importing_response = cls.model_importing_cmd(repo_root=repo_root,
                                                           model_package_path=model_package_path,
                                                           task_id=subtask_id,
                                                           work_dir=subtask_workdir)

    @classmethod
    def model_importing_cmd(repo_root: str, model_package_path: str, task_id: str,
                            work_dir: str) -> backend_pb2.GeneralResp:
        cmd = [
            utils.mir_executable(), 'import-model', '--root', repo_root, '--model-package', model_package_path, '-w',
            work_dir, '--dst-rev', f"{task_id}@{task_id}"
        ]
        return utils.run_command(cmd)


# 压缩包
#   模型文件
#   是否是同一个检测目标，需要用户自己确定，前端需要提醒
#   自己平台主出的模型文件是一定要支持的
#   用户自己的模型，只要满足前端所描述的条件，就可以导入并且可用
# 我需要给前端关于此的描述

# COPY：COPY一个模型生成一个新的BRANCH分支，已经完成
# IMPORT：