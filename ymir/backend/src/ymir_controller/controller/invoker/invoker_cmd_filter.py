from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class FilterBranchInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return True

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(invoker=self,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_DST_DATASET_ID,
                                         checker.Prerequisites.CHECK_SINGLE_IN_DATASET_ID,
                                     ])

    def invoke(self) -> backend_pb2.GeneralResp:
        if not self._user_labels:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid _user_labels")

        # invoke command
        filter_command = [
            utils.mir_executable(), 'filter', '--root', self._repo_root, '--dst-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.dst_dataset_id, tid=self._task_id), '--src-revs',
            revs.join_tvt_branch_tid(branch_id=self._request.in_dataset_ids[0], tid=self._request.his_task_id), '-w',
            self._work_dir, '--user-label-file', self._label_storage_file
        ]

        if self._request.in_class_ids:
            filter_command.append('--cis')
            filter_command.append(';'.join(
                self._user_labels.main_name_for_ids(class_ids=list(self._request.in_class_ids))))
        if self._request.ex_class_ids:
            filter_command.append('--ex-cis')
            filter_command.append(';'.join(
                self._user_labels.main_name_for_ids(class_ids=list(self._request.ex_class_ids))))
        filter_command.extend(['--filter-anno-src', utils.annotation_type_str(self._request.annotation_type)])
        return utils.run_command(filter_command)
