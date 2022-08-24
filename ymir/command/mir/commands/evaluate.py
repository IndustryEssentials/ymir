import argparse
import logging

from mir.commands import base
from mir.tools import checker, mir_storage_ops, revs_parser
from mir.tools.class_ids import ClassIdManager
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.protos import mir_command_pb2 as mirpb


class CmdEvaluate(base.BaseCommand):
    def run(self) -> int:
        logging.info(f"command evaluate: {self.args}")

        return CmdEvaluate.run_with_args(work_dir=self.args.work_dir,
                                         src_revs=self.args.src_revs,
                                         dst_rev=self.args.dst_rev,
                                         mir_root=self.args.mir_root,
                                         conf_thr=self.args.conf_thr,
                                         iou_thrs=self.args.iou_thrs,
                                         need_pr_curve=self.args.need_pr_curve,
                                         cis=self.args.cis)

    @staticmethod
    @command_run_in_out
    def run_with_args(work_dir: str, src_revs: str, dst_rev: str, mir_root: str, conf_thr: float, iou_thrs: str,
                      need_pr_curve: bool, cis: str) -> int:
        src_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)
        task_id = dst_rev_tid.tid

        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.IS_CLEAN])
        if return_code != MirCode.RC_OK:
            return return_code

        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_metadatas, mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=src_rev_tid.rev,
            mir_task_id=src_rev_tid.tid,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS])

        # save and commit
        cls_ids = ClassIdManager(mir_root=mir_root).id_for_names(names=cis.split(';'))[0] if cis else []
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeEvaluate,
                                           task_id=task_id,
                                           message='evaluate',
                                           src_revs=src_revs,
                                           dst_rev=dst_rev)
        build_config = mir_storage_ops.MirStorageOpsBuildConfig(evaluate_conf_thr=conf_thr,
                                                                evaluate_iou_thrs=iou_thrs,
                                                                evaluate_need_pr_curve=need_pr_curve,
                                                                evaluate_src_dataset_id=src_rev_tid.rev_tid,
                                                                evaluate_class_ids=cls_ids)
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_rev_tid.rev,
                                                      his_branch=src_rev_tid.rev,
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task,
                                                      build_config=build_config)

        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    evaluate_arg_parser = subparsers.add_parser('evaluate',
                                                parents=[parent_parser],
                                                description='use this command to evaluate model with ground truth',
                                                help='evaluate model with ground truth')
    evaluate_arg_parser.add_argument('-w', dest='work_dir', type=str, help='work place for training')
    evaluate_arg_parser.add_argument("--src-revs", dest="src_revs", type=str, required=True, help="rev@tid")
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
                                     default='0.5:1.0:0.05',
                                     help='iou thresholds, default 0.5:1.0:0.05, upper bound is excluded')
    evaluate_arg_parser.add_argument('--need-pr-curve',
                                     dest='need_pr_curve',
                                     action='store_true',
                                     help='also generates pr curve in evaluation result')
    # FIXME: using cis in prediction target
    evaluate_arg_parser.add_argument('--cis',
                                     dest='cis',
                                     required=False,
                                     type=str,
                                     default='',
                                     help='class names in mAP cauculate, keep empty to use all classes in gt')
    evaluate_arg_parser.set_defaults(func=CmdEvaluate)
