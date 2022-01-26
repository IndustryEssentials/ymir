import os
import threading
from typing import Dict

from common_utils.percent_log_util import LogState
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, tasks_util, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskBaseInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.TASK_CREATE
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        self._task_monitor_file = os.path.join(self._work_dir, 'out', 'monitor.txt')

        if self._async_mode:
            thread = threading.Thread(target=self._task_invoke,
                                      args=(
                                          self._sandbox_root,
                                          self._repo_root,
                                          self._assets_config,
                                          self._work_dir,
                                          self._task_monitor_file,
                                          self._request,
                                      ),
                                      daemon=True)
            thread.start()
            return utils.make_general_response(CTLResponseCode.CTR_OK, "")
        else:
            return self._task_invoke(sandbox_root=self._sandbox_root,
                                     repo_root=self._repo_root,
                                     assets_config=self._assets_config,
                                     working_dir=self._work_dir,
                                     task_monitor_file=self._task_monitor_file,
                                     request=self._request)

    @classmethod
    def _task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str], working_dir: str,
                     task_monitor_file: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        tasks_util.write_task_progress(monitor_file=task_monitor_file,
                                       tid=request.task_id,
                                       percent=0.0,
                                       state=LogState.RUNNING)
        if not request.req_create_task.no_task_monitor:
            tasks_util.register_monitor_log(
                task_id=request.task_id,
                user_id=request.user_id,
                log_paths=[task_monitor_file],
            )

        response = cls.task_invoke(sandbox_root=sandbox_root,
                                   repo_root=repo_root,
                                   assets_config=assets_config,
                                   working_dir=working_dir,
                                   task_monitor_file=task_monitor_file,
                                   request=request)
        return response

    @classmethod
    def task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str], working_dir: str,
                    task_monitor_file: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        raise NotImplementedError
