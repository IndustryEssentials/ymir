from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, code, revs, utils
from proto import backend_pb2


class MergeInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        if not self._request.in_dataset_ids and not self._request.ex_dataset_ids:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ,
                                               'one of include/exclude branches is required.')

        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_DST_TASK_ID,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        if self._request.req_type != backend_pb2.CMD_MERGE:
            raise RuntimeError("Mismatched req_type")

        command = "cd {0} && {1} merge --dst-rev {2} -s stop".format(
            self._repo_root, utils.mir_executable(),
            revs.join_tvt_branch_tid(branch_id=self._request.dst_task_id, tid=self._task_id))

        if self._request.in_dataset_ids:
            command += " --src-revs '{}'".format(
                revs.build_src_revs(in_src_revs=self._request.in_dataset_ids, his_tid=self._request.his_task_id))
        if self._request.ex_dataset_ids:
            command += " --ex-src-revs '{}'".format(revs.build_src_revs(in_src_revs=self._request.ex_dataset_ids))
        return utils.run_command(command)

    def _repr(self) -> str:
        return "cmd merge user: {0}, repo: {1}, task_id: {2} includes: {3}, excludes: {4}".format(
            self._request.user_id, self._request.repo_id, self._task_id, ";".join(self._request.in_dataset_ids),
            ";".join(self._request.ex_dataset_ids))
