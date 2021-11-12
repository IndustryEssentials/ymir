from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, code, revs, utils
from ymir.ids import class_ids
from ymir.protos import mir_controller_service_pb2 as mirsvrpb


class FilterBranchInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> mirsvrpb.GeneralResp:
        if not self._request.in_class_ids and not self._request.ex_class_ids:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ,
                                               'one of include/exclude ids is required.')

        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_DST_TASK_ID,
                                         checker.Prerequisites.CHECK_SINGLE_IN_DATASET_ID,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> mirsvrpb.GeneralResp:
        if self._request.req_type != mirsvrpb.CMD_FILTER:
            raise RuntimeError("Mismatched req_type")

        # invoke command
        filter_command = "cd {0} && {1} filter --dst-rev {2} --src-revs {3}".format(
            self._repo_root, utils.mir_executable(),
            revs.join_tvt_branch_tid(branch_id=self._request.dst_task_id, tid=self._task_id),
            revs.join_tvt_branch_tid(branch_id=self._request.in_dataset_ids[0], tid=self._request.his_task_id))

        ids_manager = class_ids.ClassIdManager()
        if self._request.in_class_ids:
            filter_command += " -p '{}'".format(';'.join(
                [ids_manager.main_name_for_id(x) for x in self._request.in_class_ids]))
        if self._request.ex_class_ids:
            filter_command += " -P '{}'".format(';'.join(
                [ids_manager.main_name_for_id(x) for x in self._request.ex_class_ids]))
        return utils.run_command(filter_command)

    def _repr(self) -> str:
        return ("filter: user: {}, repo: {}, task_id: {} in_class_ids: {}, ex_class_ids: {}"
                " in_dataset_ids: {}".format(self._request.user_id, self._request.repo_id, self._task_id,
                                             self._request.in_class_ids, self._request.ex_class_ids,
                                             self._request.in_dataset_ids))
