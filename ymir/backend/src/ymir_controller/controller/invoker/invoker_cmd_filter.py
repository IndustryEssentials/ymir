from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class FilterBranchInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_DST_DATASET_ID,
                                         checker.Prerequisites.CHECK_SINGLE_IN_DATASET_ID,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_FILTER
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        # invoke command
        filter_command = [
            utils.mir_executable(), 'filter', '--root', self._repo_root, '--dst-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.dst_dataset_id, tid=self._task_id), '--src-revs',
            revs.join_tvt_branch_tid(branch_id=self._request.in_dataset_ids[0], tid=self._request.his_task_id), '-w',
            self._work_dir
        ]

        if self._request.in_class_ids:
            filter_command.append('-p')
            filter_command.append(';'.join(
                self._user_labels.get_main_names(class_ids=list(self._request.in_class_ids))))
        if self._request.ex_class_ids:
            filter_command.append('-P')
            filter_command.append(';'.join(
                self._user_labels.get_main_names(class_ids=list(self._request.ex_class_ids))))
        return utils.run_command(filter_command)
