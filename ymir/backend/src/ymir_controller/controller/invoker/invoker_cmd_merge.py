from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class MergeInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        if not self._request.in_dataset_ids and not self._request.ex_dataset_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               'one of include/exclude branches is required.')

        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_DST_DATASET_ID,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_MERGE
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        command = [
            utils.mir_executable(), 'merge', '--root', self._repo_root, '--dst-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.dst_dataset_id, tid=self._task_id), '-s',
            backend_pb2.MergeStrategy.Name(self._request.merge_strategy).lower(), '-w', self._work_dir,
        ]

        if self._request.in_dataset_ids:
            command.append('--src-revs')
            command.append(
                revs.build_src_revs(in_src_revs=self._request.in_dataset_ids, his_tid=self._request.his_task_id))
        if self._request.ex_dataset_ids:
            command.append('--ex-src-revs')
            command.append(revs.build_src_revs(in_src_revs=self._request.ex_dataset_ids))
        return utils.run_command(command)
