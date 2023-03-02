from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils
from id_definition.error_codes import CTLResponseCode
from mir.tools.eval.eval_ctl_ops import evaluate_datasets
from mir.tools.revs_parser import parse_single_arg_rev
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
        if not (0 <= ec.conf_thr <= 1):
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED,
                                               f"invalid evaluate conf thr: {ec.conf_thr:.2f}")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    def invoke(self) -> backend_pb2.GeneralResp:
        rev_tid = parse_single_arg_rev(self._request.in_dataset_ids[0], need_tid=False)

        evaluation = evaluate_datasets(mir_root=self._repo_root,
                                       gt_rev_tid=rev_tid,
                                       pred_rev_tid=rev_tid,
                                       evaluate_config=self._request.evaluate_config)
        if not evaluation:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "no result generated.")
        response = backend_pb2.GeneralResp()
        response.code = CTLResponseCode.CTR_OK
        response.evaluation.CopyFrom(evaluation)
        return response

    def _parse_response(self, response: backend_pb2.GeneralResp) -> str:
        return f"Evaluation result config: {response.evaluation.config}"
