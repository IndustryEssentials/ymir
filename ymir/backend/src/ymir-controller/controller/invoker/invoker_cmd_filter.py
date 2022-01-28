from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, revs, utils, labels
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class FilterBranchInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        if not self._request.in_class_ids and not self._request.ex_class_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
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

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_FILTER
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        # invoke command
        filter_command = "cd \'{0}\' && {1} filter --dst-rev {2} --src-revs {3} -w \'{4}\'".format(
            self._repo_root, utils.mir_executable(),
            revs.join_tvt_branch_tid(branch_id=self._request.dst_task_id, tid=self._task_id),
            revs.join_tvt_branch_tid(branch_id=self._request.in_dataset_ids[0], tid=self._request.his_task_id),
            self._work_dir)

        label_handler = labels.LabelFileHandler(self._user_root)
        if self._request.in_class_ids:
            filter_command += " -p '{}'".format(';'.join(
                label_handler.get_main_labels_by_ids(self._request.in_class_ids)))
        if self._request.ex_class_ids:
            filter_command += " -P '{}'".format(';'.join(
                label_handler.get_main_labels_by_ids(self._request.ex_class_ids)))
        return utils.run_command(filter_command)
