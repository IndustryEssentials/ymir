from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, revs, utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class EvaluateInvoker(BaseMirControllerInvoker):
    """
    invoker for command evaluate
    request.in_dataset_ids: predictions
    request.singleton_op: ground truth
    request.task_id: task hash for this evaluate command
    request.evaluate_config.conf_thr: confidence threshold
    request.evaluate_config.iou_thrs_interval: from:to:step, default is '0.5:1.0:0.05', end point excluded
    """
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        checker_resp = checker.check_request(request=self._request,
                                             prerequisites=[
                                                 checker.Prerequisites.CHECK_USER_ID,
                                                 checker.Prerequisites.CHECK_REPO_ID,
                                                 checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                                 checker.Prerequisites.CHECK_TASK_ID,
                                                 checker.Prerequisites.CHECK_SINGLETON_OP,
                                                 checker.Prerequisites.CHECK_IN_DATASET_IDS,
                                             ],
                                             mir_root=self._repo_root)
        if checker_resp.code != CTLResponseCode.CTR_OK:
            return checker_resp

        conf_thr = self._request.evaluate_config.conf_thr
        if conf_thr < 0 or conf_thr >= 1:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               f"invalid evaluate conf thr: {conf_thr:.2f}")

        iou_thrs_interval: str = self._request.evaluate_config.iou_thrs_interval or '0.5:1.0:0.05'
        iou_thrs_interval_list = [float(v) for v in iou_thrs_interval.split(':')]
        if len(iou_thrs_interval_list) != 3:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               "invalid evaluate iou thrs interval: {}".format(iou_thrs_interval))
        for v in iou_thrs_interval_list:
            if v < 0 or v > 1:
                return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                                   "invalid evaluate iou thrs interval: {}".format(iou_thrs_interval))

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    def invoke(self) -> backend_pb2.GeneralResp:
        expected_type = backend_pb2.RequestType.CMD_EVALUATE
        if self._request.req_type != expected_type:
            return utils.make_general_response(CTLResponseCode.MIS_MATCHED_INVOKER_TYPE,
                                               f"expected: {expected_type} vs actual: {self._request.req_type}")

        ec = self._request.evaluate_config
        command = [
            utils.mir_executable(),
            'evaluate',
            '--root',
            self._repo_root,
            '--dst-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.task_id, tid=self._request.task_id),
            '--src-revs',
            revs.build_src_revs(in_src_revs=self._request.in_dataset_ids, his_tid=self._request.his_task_id),
            '--gt-rev',
            revs.join_tvt_branch_tid(branch_id=self._request.singleton_op, tid=self._request.singleton_op),
            '-w',
            self._work_dir,
            '--conf-thr',
            f"{ec.conf_thr:.2f}",
            '--iou-thrs',
            ec.iou_thrs_interval,
        ]
        if ec.need_pr_curve:
            command.append('--need-pr-curve')

        return utils.run_command(command)
