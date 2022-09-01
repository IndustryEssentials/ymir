from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from mir.tools import det_eval_ctl_ops, revs_parser
from proto import backend_pb2


class EvaluateInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        checker_resp = checker.check_invoker(invoker=self,
                                             prerequisites=[
                                                 checker.Prerequisites.CHECK_USER_ID,
                                                 checker.Prerequisites.CHECK_REPO_ID,
                                                 checker.Prerequisites.CHECK_REPO_ROOT_EXIST,
                                                 checker.Prerequisites.CHECK_TASK_ID,
                                                 checker.Prerequisites.CHECK_IN_DATASET_IDS,
                                             ])
        if checker_resp.code != CTLResponseCode.CTR_OK:
            return checker_resp

        ec = self._request.evaluate_config
        if ec.conf_thr < 0 or ec.conf_thr >= 1:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               f"invalid evaluate conf thr: {ec.conf_thr:.2f}")

        if not ec.iou_thrs_interval:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               "invalid evaluate iou thrs interval: {}".format(ec.iou_thrs_interval))

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    def invoke(self) -> backend_pb2.GeneralResp:
        ec = self._request.evaluate_config
        rev_tid = revs_parser.parse_single_arg_rev(self._request.in_dataset_ids[0], need_tid=False)

        evaluation = det_eval_ctl_ops.det_evaluate_datasets(mir_root=self._repo_root,
                                                            gt_rev_tid=rev_tid,
                                                            pred_rev_tid=rev_tid,
                                                            conf_thr=ec.conf_thr,
                                                            iou_thrs=ec.iou_thrs_interval,
                                                            need_pr_curve=ec.need_pr_curve)

        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        response.evaluation.CopyFrom(evaluation)
        return response
