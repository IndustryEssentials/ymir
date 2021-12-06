from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.task_monitor import ControllerTaskMonitor
from controller.utils import checker, code, utils
from proto import backend_pb2


class GetTaskInfoInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request, prerequisites=[
            checker.Prerequisites.CHECK_TASKINFO_IDS,
        ])

    def invoke(self) -> backend_pb2.GeneralResp:
        resp = utils.make_general_response(code.ResCode.CTR_OK, "")
        task_monitor = ControllerTaskMonitor(storage_root='')
        for task_id in self._request.req_get_task_info.task_ids:
            task_item = task_monitor.load_task(task_id)

            resp.resp_get_task_info.task_infos[task_id].CopyFrom(task_item.general_info)
        return resp

    def _repr(self) -> str:
        return "get_task_infos: {0} user: {1} tasks: {2}".format(self._request.req_get_task_info.task_ids,
                                                                 self._request.user_id,
                                                                 self._request.req_get_task_info.task_ids)
