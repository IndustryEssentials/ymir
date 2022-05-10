import argparse
import logging

import numpy as np

from mir.commands import base
from mir.tools import checker, eval, mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


class CmdEvaluate(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command evaluate: %s", self.args)

        return CmdEvaluate.run_with_args(work_dir=self.args.work_dir,
                                         src_revs=self.args.src_revs,
                                         dst_rev=self.args.dst_rev,
                                         gt_rev=self.args.gt_rev,
                                         mir_root=self.args.mir_root,
                                         conf_thr=self.args.conf_thr,
                                         iou_thr_from=self.args.iou_thr_from,
                                         iou_thr_to=self.args.iou_thr_to,
                                         iou_thr_step=self.args.iou_thr_step)

    @staticmethod
    @command_run_in_out
    def run_with_args(work_dir: str, src_revs: str, dst_rev: str, gt_rev: str, mir_root: str, conf_thr: float,
                      iou_thr_from: float, iou_thr_to: float, iou_thr_step: float) -> int:
        src_rev_tids = revs_parser.parse_arg_revs(src_revs)
        gt_rev_tid = revs_parser.parse_single_arg_rev(gt_rev, need_tid=False)
        dst_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.IS_CLEAN])
        if return_code != MirCode.RC_OK:
            return return_code

        for thr in [conf_thr, iou_thr_from, iou_thr_to, iou_thr_step]:
            if thr < 0 or thr > 1:
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                      error_message='invalid conf_thr, iou_thr_from, iou_thr_to or iou_thr_step')
        if iou_thr_from >= iou_thr_to:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='invalid iou_thr_from or iou_thr_to')

        # read pred and gt
        mir_preds = [eval.MirCoco(mir_root=mir_root, rev_tid=src_rev_tid) for src_rev_tid in src_rev_tids]
        mir_gt = eval.MirCoco(mir_root=mir_root, rev_tid=gt_rev_tid)

        # check pred and gt
        for mir_pred in mir_preds:
            if len(mir_pred.mir_metadatas.attributes) == 0:
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='no assets in predictions')
            if set(mir_pred.mir_metadatas.attributes.keys()) != set(mir_gt.mir_metadatas.attributes.keys()):
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                      error_message='prediction and ground truth have different assets')
            pred_annotations = mir_pred.mir_annotations.task_annotations[
                mir_pred.mir_annotations.head_task_id].image_annotations
            if not pred_annotations:
                raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                      error_message='prediction annotations empty')
        gt_annotations = mir_gt.mir_annotations.task_annotations[mir_gt.mir_annotations.head_task_id].image_annotations
        if not gt_annotations:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='ground truth annotations empty')

        # eval
        evaluation = _evaluate_with_cocotools(mir_pred=mir_pred,
                                              mir_gt=mir_gt,
                                              conf_thr=conf_thr,
                                              iou_thr_from=iou_thr_from,
                                              iou_thr_to=iou_thr_to,
                                              iou_thr_step=iou_thr_step)

        # save and commit
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeEvaluate,
                                           task_id=dst_rev_tid.tid,
                                           message='evaluate',
                                           evaluation=evaluation,
                                           src_revs=src_revs,
                                           dst_rev=dst_rev)
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_rev_tid.rev,
                                                      his_branch=src_rev_tid.rev,
                                                      mir_datas={},
                                                      task=task)

        return MirCode.RC_OK


def _evaluate_with_cocotools(mir_pred: eval.MirCoco, mir_gt: eval.MirCoco, conf_thr: float, iou_thr_from: float,
                             iou_thr_to: float, iou_thr_step: float) -> mirpb.Evaluation:
    params = eval.Params()
    params.confThr = conf_thr
    params.iouThrs = np.linspace(start=iou_thr_from,
                                 stop=iou_thr_to,
                                 num=int(np.round((iou_thr_to - iou_thr_from) / iou_thr_step)) + 1,
                                 endpoint=True)

    evaluator = eval.MirEval(coco_gt=mir_gt, coco_dt=mir_pred, params=params)
    evaluator.evaluate()
    evaluator.accumulate()

    return evaluator.get_evaluation_result()


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    evaluate_arg_parser = subparsers.add_parser('evaluate',
                                                parents=[parent_parser],
                                                description='use this command to evaluate model with ground truth',
                                                help='evaluate model with ground truth')
    evaluate_arg_parser.add_argument('-w', dest='work_dir', type=str, help='work place for training')
    evaluate_arg_parser.add_argument("--src-revs", dest="src_revs", type=str, required=True, help="prediction rev@tid")
    evaluate_arg_parser.add_argument("--gt-rev", dest="gt_rev", type=str, required=True, help="ground truth rev@tid")
    evaluate_arg_parser.add_argument("--dst-rev",
                                     dest="dst_rev",
                                     type=str,
                                     required=True,
                                     help="rev@tid: destination branch name and task id")
    evaluate_arg_parser.add_argument('--conf-thr',
                                     dest='conf_thr',
                                     type=float,
                                     required=False,
                                     default=0.3,
                                     help='confidence threshold, default 0.3')
    evaluate_arg_parser.add_argument('--iou-thr-from',
                                     dest='iou_thr_from',
                                     type=float,
                                     required=False,
                                     default=0.5,
                                     help='min iou threshold, default 0.5')
    evaluate_arg_parser.add_argument('--iou-thr-to',
                                     dest='iou_thr_to',
                                     type=float,
                                     required=False,
                                     default=0.95,
                                     help='max iou threshold, default 0.95')
    evaluate_arg_parser.add_argument('--iou-thr-step',
                                     dest='iou_thr_step',
                                     type=float,
                                     required=False,
                                     default=0.05,
                                     help='iou threshold step, default 0.95')
    evaluate_arg_parser.set_defaults(func=CmdEvaluate)
