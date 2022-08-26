from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, revs, utils
from proto import backend_pb2


class SamplingInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return True

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(invoker=self,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_DST_DATASET_ID,
                                         checker.Prerequisites.CHECK_TASK_ID,
                                     ])

    def invoke(self) -> backend_pb2.GeneralResp:
        command = [
            utils.mir_executable(),
            'sampling',
            '--root',
            self._repo_root,
            '--dst-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.dst_dataset_id, tid=self._request.task_id),
            '--src-revs',
            revs.join_tvt_branch_tid(branch_id=self._request.in_dataset_ids[0], tid=self._request.his_task_id),
            '-w',
            self._work_dir,
        ]
        if self._request.sampling_count:
            command.extend(['--count', str(self._request.sampling_count)])
        elif self._request.sampling_rate:
            command.extend(['--rate', str(self._request.sampling_rate)])

        return utils.run_command(command)
