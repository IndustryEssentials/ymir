import logging
import os
import threading
from typing import Dict, List

import yaml

from common_utils.labels import UserLabels
from common_utils.percent_log_util import LogState, PercentLogHandler
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, errors, gpu_utils, tasks_util, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskBaseInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        # still in sync mode.
        checker_ret = checker.check_request(request=self._request,
                                            prerequisites=[
                                                checker.Prerequisites.CHECK_USER_ID,
                                                checker.Prerequisites.CHECK_REPO_ID,
                                                checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                            ],
                                            mir_root=self._repo_root)
        if checker_ret.code != CTLResponseCode.CTR_OK:
            return checker_ret
        return self.task_pre_invoke(request=self._request, sandbox_root=self._sandbox_root)

    @classmethod
    def subtask_work_dir(cls, master_work_dir: str, subtask_id: str) -> str:
        subtask_workdir = os.path.join(master_work_dir, 'sub_task', subtask_id)
        os.makedirs(subtask_workdir, exist_ok=True)
        return subtask_workdir

    @classmethod
    def subtask_monitor_file(cls, master_work_dir: str, subtask_id: str) -> str:
        subtask_workdir = cls.subtask_work_dir(
            master_work_dir=master_work_dir,
            subtask_id=subtask_id,
        )
        subtask_monitor_root = os.path.join(subtask_workdir, 'out')
        os.makedirs(subtask_monitor_root, exist_ok=True)
        sub_monitor_file = os.path.join(subtask_monitor_root, 'monitor.txt')
        return sub_monitor_file

    @classmethod
    def create_subtask_workdir_monitor(
        cls,
        task_id: str,
        user_id: str,
        master_work_dir: str,
        subtask_weights: List[float],
        register_monitor: bool,
    ) -> None:
        if not (subtask_weights and task_id and user_id and master_work_dir):
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED,
                                     "create_subtask_workdir_monitor args error, abort.")

        delta = 0.001
        if abs(sum(subtask_weights) - 1) >= delta:
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid weights, abort.")
        sub_monitor_files_weights = {}
        for idx in range(len(subtask_weights)):
            subtask_id = utils.sub_task_id(task_id, idx)
            subtask_monitor_file = cls.subtask_monitor_file(master_work_dir=master_work_dir, subtask_id=subtask_id)
            PercentLogHandler.write_percent_log(log_file=subtask_monitor_file,
                                                tid=utils.sub_task_id(task_id, idx),
                                                percent=0.0,
                                                state=LogState.RUNNING)
            sub_monitor_files_weights[subtask_monitor_file] = subtask_weights[idx]

        logging.info(f"task {task_id} logging weights:\n{sub_monitor_files_weights}\n")
        if register_monitor:
            tasks_util.register_monitor_log(
                task_id=task_id,
                user_id=user_id,
                log_path_weights=sub_monitor_files_weights,
            )
        return

    @staticmethod
    def gen_executor_config_path(work_dir: str) -> str:
        if not (work_dir and os.path.isdir(work_dir)):
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED, f"invalid work_dir: {work_dir}")
        return os.path.join(work_dir, "task_config.yaml")

    @staticmethod
    def gen_executor_config_lock_gpus(req_executor_config: str, class_names: List, task_parameters: str,
                                      output_config_file: str) -> bool:
        executor_config = yaml.safe_load(req_executor_config)
        task_context = {}

        if class_names:
            executor_config["class_names"] = class_names

        # when gpu_count > 0, use gpu model
        gpu_count = executor_config["gpu_count"]
        if gpu_count > 0:
            gpu_ids = gpu_utils.GPUInfo().find_gpu_ids_by_config(gpu_count, lock_gpu=True)
            if not gpu_ids:
                return False

            task_context["available_gpu_id"] = gpu_ids
            executor_config['gpu_id'] = ','.join([str(i) for i in range(gpu_count)])
        else:
            task_context["available_gpu_id"] = ''
            executor_config['gpu_id'] = ''

        if task_parameters:
            task_context['task_parameters'] = task_parameters

        config = {'executor_config': executor_config, 'task_context': task_context}

        with open(output_config_file, "w") as f:
            yaml.dump(config, f)

        return True

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.TASK_CREATE
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")
        self.create_subtask_workdir_monitor(task_id=self._task_id,
                                            user_id=self._user_id,
                                            master_work_dir=self._work_dir,
                                            subtask_weights=self.subtask_weights(),
                                            register_monitor=(not self._request.req_create_task.no_task_monitor))

        if self._async_mode:
            thread = threading.Thread(target=self.task_invoke,
                                      args=(
                                          self._sandbox_root,
                                          self._repo_root,
                                          self._assets_config,
                                          self._work_dir,
                                          self._user_labels,
                                          self._request,
                                      ),
                                      daemon=True)
            thread.start()
            return utils.make_general_response(CTLResponseCode.CTR_OK, "")
        else:
            return self.task_invoke(sandbox_root=self._sandbox_root,
                                    repo_root=self._repo_root,
                                    assets_config=self._assets_config,
                                    working_dir=self._work_dir,
                                    user_labels=self._user_labels,
                                    request=self._request)

    @classmethod
    def task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str], working_dir: str,
                    user_labels: UserLabels, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        subtask_weights = cls.subtask_weights()
        previous_subtask_id = None
        # revsersed, to makesure the last subtask idx is 0.
        for subtask_idx in reversed(range(len(subtask_weights))):
            logging.info(f"processing subtask {subtask_idx}")

            subtask_id = utils.sub_task_id(request.task_id, subtask_idx)
            subtask_work_dir = cls.subtask_work_dir(master_work_dir=working_dir, subtask_id=subtask_id)

            subtask_func_name = f"subtask_invoke_{subtask_idx}"
            subtask_func = getattr(cls, subtask_func_name)
            ret = subtask_func(
                sandbox_root=sandbox_root,
                repo_root=repo_root,
                assets_config=assets_config,
                request=request,
                subtask_id=subtask_id,
                subtask_workdir=subtask_work_dir,
                previous_subtask_id=previous_subtask_id,
                user_labels=user_labels,
            )
            if ret.code != CTLResponseCode.CTR_OK:
                logging.info(f"subtask failed: {subtask_func_name}\nret: {ret}")
                return ret

            previous_subtask_id = subtask_id

        return ret

    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        raise NotImplementedError

    @classmethod
    def subtask_weights(cls) -> List:
        # Subtasks are called in reversed order of index so the index 0 submask is last called,
        # as a result, the weight list should also be organized in reversed index order.
        raise NotImplementedError

    @classmethod
    def subtask_invoke_2(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        raise NotImplementedError

    @classmethod
    def subtask_invoke_1(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        raise NotImplementedError

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        raise NotImplementedError
