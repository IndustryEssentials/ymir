from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class EvaluateInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                         checker.Prerequisites.CHECK_DST_DATASET_ID,
                                         checker.Prerequisites.CHECK_TASK_ID,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_EVALUATE
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        command = [
            utils.mir_executable(),
            'evaluate',
            '--root',
            self._repo_root,
            '--dst-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.dst_dataset_id, tid=self._request.task_id),
            '--src-revs',
            revs.build_src_revs(in_src_revs=self._request.in_dataset_ids, his_tid=self._request.his_task_id),
            '--gt-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.singleton_op, tid=self._request.singleton_op),
            '-w',
            self._work_dir,
            '--conf-thr',
            f"{self._request.evaluate_config.conf_threshold:.2f}",
            '--iou-thr-from',
            f"{self._request.evaluate_config.iou_threshold_from:.2f}",
            '--iou-thr-to',
            f"{self._request.evaluate_config.iou_threshold_to:.2f}",
            '--iou-thr-step',
            f"{self._request.evaluate_config.iou_threshold_step:.2f}",
        ]

        return utils.run_command(command)
