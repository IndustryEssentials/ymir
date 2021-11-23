import os
import threading
from functools import wraps
from typing import Any, Callable, Dict

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.task_monitor import ControllerTaskMonitor
from controller.utils import code, checker, tasks_util, utils
from proto import backend_pb2


def write_done_progress(fn: Callable) -> Callable:
    @wraps(fn)
    def write_done(*args: tuple, **kwargs: Any) -> Any:
        ret = fn(*args, **kwargs)
        print('ret: {}'.format(ret))
        tasks_util.write_task_progress(kwargs['task_monitor_file'], kwargs['request'].task_id, 1.0,
                                       backend_pb2.TaskStateDone)
        return ret

    return write_done


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
        if self._request.req_type != backend_pb2.TASK_CREATE:
            raise RuntimeError("Mismatched req_type")

        self._task_monitor_file = os.path.join(self._work_dir, 'out', 'monitor.txt')

        if not self._request.req_create_task.no_task_monitor:
            task_monitor = ControllerTaskMonitor(storage_root='')
            task_monitor.register_task(task_id=self._request.task_id,
                                       repo_root=self._repo_root,
                                       task_monitor_file=self._task_monitor_file,
                                       request=self._request)

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
            return utils.make_general_response(code.ResCode.CTR_OK, "")
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
                                       state=backend_pb2.TaskStateRunning)

        response = cls.task_invoke(sandbox_root=sandbox_root,
                                   repo_root=repo_root,
                                   assets_config=assets_config,
                                   working_dir=working_dir,
                                   task_monitor_file=task_monitor_file,
                                   request=request)

        # write error message.
        if response.code != code.ResCode.CTR_OK:
            tasks_util.write_task_progress(monitor_file=task_monitor_file,
                                           tid=request.task_id,
                                           percent=1.0,
                                           state=backend_pb2.TaskStateError,
                                           msg=response.message)

        return response

    @classmethod
    def task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str], working_dir: str,
                    task_monitor_file: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        raise NotImplementedError

    def _repr(self) -> str:
        return "create_task_base: user: {}, repo: {} task_type: {}".format(self._request.user_id, self._request.repo_id,
                                                                           self._request.req_create_task.task_type)
