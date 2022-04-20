import argparse
import logging
from typing import Any
from mir.tools.errors import MirRuntimeError

from mir.commands import base
from mir.tools import checker, eval, mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.protos import mir_command_pb2 as mirpb


class CmdEvaluate(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command evaluate: %s", self.args)

        return CmdEvaluate.run_with_args(work_dir=self.args.work_dir,
                                         src_revs=self.args.src_revs,
                                         dst_rev=self.args.dst_rev,
                                         mir_root=self.args.mir_root)

    @staticmethod
    @command_run_in_out
    def run_with_args(work_dir: str, src_revs: str, dst_rev: str, mir_root: str) -> int:
        src_rev_tid, gt_rev_tid = revs_parser.parse_arg_revs(src_revs)  # pred and gt
        dst_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.IS_CLEAN])
        if return_code != MirCode.RC_OK:
            return return_code

        # read pred and gt
        mir_pred = eval.MirCoco(mir_root=mir_root, rev_tid=src_rev_tid)
        mir_gt = eval.MirCoco(mir_root=mir_root, rev_tid=gt_rev_tid)

        # check pred and gt
        if len(mir_pred.mir_metadatas.attributes) == 0:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='no assets in predictions')
        if set(mir_pred.mir_metadatas.attributes.keys()) != set(mir_gt.mir_metadatas.attributes.keys()):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='prediction and ground truth have different assets list')

        # eval
        evaluate_result = _evaluate_with_cocotools(mir_pred=mir_pred, mir_gt=mir_gt)

        # save and commit
        logging.info(f"eval result: {evaluate_result}")

        return MirCode.RC_OK


def _evaluate_with_cocotools(mir_pred: eval.MirCoco, mir_gt: eval.MirCoco) -> Any:
    evaluator = eval.MirEval(coco_gt=mir_gt, coco_dt=mir_pred)
    # evaluator.evaluate()
    # evaluator.accumulate()
    # evaluator.summarize()
    # return evaluator.stats


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    evaluate_arg_parser = subparsers.add_parser("evaluate",
                                                parents=[parent_parser],
                                                description="use this command to evaluate model with ground truth",
                                                help="evaluate model with ground truth")
    evaluate_arg_parser.add_argument("-w", dest="work_dir", type=str, help="work place for training")
    evaluate_arg_parser.add_argument("--src-revs",
                                     dest="src_revs",
                                     type=str,
                                     required=True,
                                     help="prediction rev@tid and ground truth rev@tid, seperated by semicolons")
    evaluate_arg_parser.add_argument("--dst-rev",
                                     dest="dst_rev",
                                     type=str,
                                     required=True,
                                     help="rev@tid: destination branch name and task id")
    evaluate_arg_parser.set_defaults(func=CmdEvaluate)