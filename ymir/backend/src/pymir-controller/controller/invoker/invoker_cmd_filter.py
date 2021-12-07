import os

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, code, revs, utils, labels
from proto import backend_pb2


class FilterBranchInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
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

    # check father filter task
    def check_filter_task_work_dir(self):
        father_task_type = backend_pb2.TaskType.Name(backend_pb2.TaskType.TaskTypeFilter)
        father_work_dir = os.path.join(self._sandbox_root, "work_dir", father_task_type, self._request.dst_task_id)
        if os.path.exists(father_work_dir):
            return father_work_dir
        else:
            return False

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_FILTER:
            raise RuntimeError("Mismatched req_type")

        # invoke command
        filter_command = "cd {0} && {1} filter --dst-rev {2} --src-revs {3}".format(
            self._repo_root, utils.mir_executable(),
            revs.join_tvt_branch_tid(branch_id=self._request.dst_task_id, tid=self._task_id),
            revs.join_tvt_branch_tid(branch_id=self._request.in_dataset_ids[0], tid=self._request.his_task_id))

        label_handler = labels.LabelFileHandler(self._user_root)
        if self._request.in_class_ids:
            filter_command += " -p '{}'".format(';'.join(label_handler.get_main_labels_by_ids(self._request.in_class_ids)))
        if self._request.ex_class_ids:
            filter_command += " -P '{}'".format(';'.join(label_handler.get_main_labels_by_ids(self._request.ex_class_ids)))

        father_work_dir = self.check_filter_task_work_dir()
        if father_work_dir:
            filter_command += f" -w {father_work_dir}"

        return utils.run_command(filter_command)

    def _repr(self) -> str:
        return ("filter: user: {}, repo: {}, task_id: {} in_class_ids: {}, ex_class_ids: {}"
                " in_dataset_ids: {}".format(self._request.user_id, self._request.repo_id, self._task_id,
                                             self._request.in_class_ids, self._request.ex_class_ids,
                                             self._request.in_dataset_ids))
