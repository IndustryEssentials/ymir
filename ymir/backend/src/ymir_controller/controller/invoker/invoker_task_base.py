from distutils.util import strtobool
import logging
import os
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

import yaml

from common_utils.labels import UserLabels
from common_utils.percent_log_util import LogState, PercentLogHandler
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, errors, gpu_utils, tasks_util, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


SubTaskType = Callable[
    [backend_pb2.GeneralReq, UserLabels, str, Dict[str, str], str, str, str, str, Optional[str], List[str]],
    backend_pb2.GeneralResp]


class TaskBaseInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return True

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        # still in sync mode.
        checker_ret = checker.check_invoker(invoker=self,
                                            prerequisites=[
                                                checker.Prerequisites.CHECK_USER_ID,
                                                checker.Prerequisites.CHECK_REPO_ID,
                                                checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                            ])
        if checker_ret.code != CTLResponseCode.CTR_OK:
            return checker_ret
        return self.task_pre_invoke(request=self._request)

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
    def _register_subtask_monitor(
        cls,
        task_id: str,
        master_work_dir: str,
        sub_task_id_weights: Dict[str, float],
        register_monitor: bool,
    ) -> None:
        if not (sub_task_id_weights and task_id and master_work_dir):
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED,
                                     "_register_subtask_monitor args error, abort.")

        delta = 0.001
        if abs(sum(sub_task_id_weights.values()) - 1) >= delta:
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid weights, abort.")
        sub_monitor_files_weights = {}
        # format: (task_func, weight, sub_task_id)
        for sub_task_id in sub_task_id_weights:
            subtask_monitor_file = cls.subtask_monitor_file(master_work_dir=master_work_dir, subtask_id=sub_task_id)
            PercentLogHandler.write_percent_log(log_file=subtask_monitor_file,
                                                tid=sub_task_id,
                                                percent=0.0,
                                                state=LogState.RUNNING)
            sub_monitor_files_weights[subtask_monitor_file] = sub_task_id_weights[sub_task_id]

        logging.info(f"task {task_id} logging weights:\n{sub_monitor_files_weights}\n")
        if register_monitor:
            tasks_util.register_monitor_log(task_id=task_id, log_path_weights=sub_monitor_files_weights)
        return

    @staticmethod
    def gen_executor_config_path(work_dir: str) -> str:
        if not (work_dir and os.path.isdir(work_dir)):
            raise errors.MirCtrError(CTLResponseCode.ARG_VALIDATION_FAILED, f"invalid work_dir: {work_dir}")
        return os.path.join(work_dir, "task_config.yaml")

    @staticmethod
    def gen_executor_config_lock_gpus(req_executor_config: str,
                                      class_names: List,
                                      output_config_file: str,
                                      assets_config: Dict = {},
                                      preprocess: Optional[str] = None) -> bool:
        executor_config = yaml.safe_load(req_executor_config)
        preprocess_config = yaml.safe_load(preprocess) if preprocess else None
        task_context: Dict[str, Any] = {}

        if class_names:
            executor_config["class_names"] = class_names

        if preprocess_config:
            task_context["preprocess"] = preprocess_config

        task_context['server_runtime'] = assets_config['server_runtime']

        gpu_count = executor_config.get("gpu_count", 0)
        executor_config["gpu_id"] = ",".join([str(i) for i in range(gpu_count)])

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
            gpu_ids = gpu_utils.GPUInfo().find_gpu_ids_by_config(gpu_count, lock_gpu=True)
            if gpu_ids is None:
                return False
            task_context["available_gpu_id"] = gpu_ids

        with open(output_config_file, "w") as f:
            yaml.safe_dump(dict(
                executor_config=executor_config,
                task_context=task_context,
            ), f)

        return True

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._async_mode:
            thread = threading.Thread(target=self.task_invoke,
                                      args=(
                                          self._task_id,
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
            return self.task_invoke(task_id=self._task_id,
                                    sandbox_root=self._sandbox_root,
                                    repo_root=self._repo_root,
                                    assets_config=self._assets_config,
                                    working_dir=self._work_dir,
                                    user_labels=self._user_labels,
                                    request=self._request)

    @classmethod
    def task_invoke(cls, task_id: str, sandbox_root: str, repo_root: str, assets_config: Dict[str,
                                                                                              str], working_dir: str,
                    user_labels: UserLabels, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        sub_tasks = cls.register_subtasks(request)
        if not sub_tasks:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, 'empty ops')

        # append subtask_id, in revsersed order, to make sure the last subtask idx is 0.
        # format: (task_func, weight, sub_task_id)
        sub_tasks_join = [(sub_task[0], sub_task[1], utils.sub_task_id(request.task_id,
                                                                       len(sub_tasks) - 1 - subtask_idx))
                          for subtask_idx, sub_task in enumerate(sub_tasks)]

        # add post_task index as last subtask with a special sub_id (i)
        if cls.need_index_repo():
            index_sub_task_id = request.task_id[0] + 'i' + request.task_id[2:]
            sub_tasks_join.append((cls._subtask_invoke_index, 0.0, index_sub_task_id))

        sub_task_id_weights: Dict[str, float] = {}
        for sub_task in sub_tasks_join:
            sub_task_id_weights[sub_task[2]] = sub_task[1]
        cls._register_subtask_monitor(task_id=task_id,
                                      master_work_dir=working_dir,
                                      sub_task_id_weights=sub_task_id_weights,
                                      register_monitor=(not request.req_create_task.no_task_monitor))

        in_dataset_ids: List[str] = request.in_dataset_ids
        his_task_id: Optional[str] = None
        if in_dataset_ids:
            his_task_id = in_dataset_ids[0]
        for sub_task in sub_tasks_join:
            subtask_id = sub_task[2]
            logging.info(f"processing subtask {subtask_id}")
            subtask_work_dir = cls.subtask_work_dir(master_work_dir=working_dir, subtask_id=subtask_id)

            ret = sub_task[0](
                request,
                user_labels,
                sandbox_root,
                assets_config,
                repo_root,
                task_id,
                subtask_id,
                subtask_work_dir,
                his_task_id,
                in_dataset_ids,
            )
            if ret.code != CTLResponseCode.CTR_OK:
                logging.info(f"subtask failed: {subtask_id}\nret: {ret}")
                return ret

            his_task_id = subtask_id
            in_dataset_ids = [task_id]

        return ret

    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        raise NotImplementedError

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        # register sub_tasks in executing orders.
        raise NotImplementedError

    @classmethod
    def need_index_repo(cls) -> bool:
        return True

    # Index master_task_id repo into viewer cached db.
    @classmethod
    def _subtask_invoke_index(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, his_task_id: Optional[str],
                              in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        index_response = utils.index_repo(user_id=request.user_id, repo_id=request.repo_id, task_id=master_task_id)
        if index_response.code == CTLResponseCode.CTR_OK:
            log_state = LogState.DONE
        else:
            log_state = LogState.ERROR
        PercentLogHandler.write_percent_log(log_file=os.path.join(subtask_workdir, 'out', 'monitor.txt'),
                                            tid=subtask_id,
                                            percent=1.0,
                                            state=log_state,
                                            msg=index_response.message)

        return index_response
