import argparse
import logging
from typing import List

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
                                         iou_thrs=self.args.iou_thrs)

    @staticmethod
    @command_run_in_out
    def run_with_args(work_dir: str, src_revs: str, dst_rev: str, gt_rev: str, mir_root: str, conf_thr: float,
                      iou_thrs: str) -> int:
        src_rev_tids = revs_parser.parse_arg_revs(src_revs)
        gt_rev_tid = revs_parser.parse_single_arg_rev(gt_rev, need_tid=False)
        dst_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.IS_CLEAN])
        if return_code != MirCode.RC_OK:
            return return_code

        iou_thrs_list = [float(v) for v in iou_thrs.split(':')]
        iou_thr_from, iou_thr_to, iou_thr_step = iou_thrs_list

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
        evaluation = _evaluate_with_cocotools(mir_preds=mir_preds,
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
                                                      his_branch=src_rev_tids[0].rev,
                                                      mir_datas={},
                                                      task=task)
        
        _show_evaluation(evaluation=evaluation)

        return MirCode.RC_OK


def _evaluate_with_cocotools(mir_preds: List[eval.MirCoco], mir_gt: eval.MirCoco, conf_thr: float, iou_thr_from: float,
                             iou_thr_to: float, iou_thr_step: float) -> mirpb.Evaluation:
    params = eval.Params()
    params.confThr = conf_thr
    params.iouThrs = np.linspace(start=iou_thr_from,
                                 stop=iou_thr_to,
                                 num=int(np.round((iou_thr_to - iou_thr_from) / iou_thr_step)) + 1,
                                 endpoint=True)

    evaluation = mirpb.Evaluation()
    evaluation.config.conf_thr = conf_thr
    evaluation.config.iou_thr_from = iou_thr_from
    evaluation.config.iou_thr_to = iou_thr_to
    evaluation.config.iou_thr_step = iou_thr_step
    evaluation.config.gt_dataset_id = mir_gt.dataset_id
    evaluation.config.pred_dataset_ids.extend([mir_pred.dataset_id for mir_pred in mir_preds])

    for mir_pred in mir_preds:
        evaluator = eval.MirEval(coco_gt=mir_gt, coco_dt=mir_pred, params=params)
        evaluator.evaluate()
        evaluator.accumulate()

        single_dataset_evaluation = evaluator.get_evaluation_result()
        single_dataset_evaluation.conf_thr = conf_thr
        single_dataset_evaluation.gt_dataset_id = mir_gt.dataset_id
        single_dataset_evaluation.pred_dataset_id = mir_pred.dataset_id
        evaluation.dataset_evaluations[mir_pred.dataset_id].CopyFrom(single_dataset_evaluation)

    return evaluation


def _show_evaluation(evaluation: mirpb.Evaluation) -> None:
    logging.info(f"\nevaluation result for ground truth: {evaluation.config.gt_dataset_id}")
    for dataset_id, dataset_evaluation in evaluation.dataset_evaluations.items():
        average_evaluation = dataset_evaluation.average_evaluation.average_ci_evaluation
        logging.info(f"    prediction: {dataset_id}, AP: {average_evaluation.ap}, AR: {average_evaluation.ar}")
    logging.info('')


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
    evaluate_arg_parser.add_argument('--iou-thrs',
                                     dest='iou_thrs',
                                     type=str,
                                     required=False,
                                     default='0.5:0.95:0.05',
                                     help='iou thresholds, default 0.5:0.95:0.05, upper bound is included')
    evaluate_arg_parser.set_defaults(func=CmdEvaluate)
