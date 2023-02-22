import argparse
import logging
from google.protobuf import json_format

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, mir_storage, mir_storage_ops, revs_parser
from mir.tools.code import MirCode


class CmdShow(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command show: %s", self.args)

        return CmdShow.run_with_args(mir_root=self.args.mir_root,
                                     src_revs=self.args.src_revs,
                                     verbose=self.args.verbose)

    @classmethod
    def run_with_args(cls, mir_root: str, src_revs: str, verbose: bool) -> int:
        # check args
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        check_code = checker.check(mir_root,
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if check_code != MirCode.RC_OK:
            return check_code

        [metadatas, annotations, keywords, tasks,
         context] = mir_storage_ops.MirStorageOps.load_multiple_storages(mir_root=mir_root,
                                                                         mir_branch=src_typ_rev_tid.rev,
                                                                         mir_task_id=src_typ_rev_tid.tid,
                                                                         ms_list=mir_storage.get_all_mir_storage(),
                                                                         as_dict=False)
        cls._show_general_metadatas(metadatas)
        cls._show_general_annotations(annotations)
        cls._show_general_context(context, keywords)
        cls._show_general_tasks(tasks, verbose)

        return MirCode.RC_OK

    @classmethod
    def _show_general_metadatas(cls, mir_metadatas: mirpb.MirMetadatas) -> None:
        un_tr_va_te_counts = [0, 0, 0, 0]
        for _, asset_attr in mir_metadatas.attributes.items():
            un_tr_va_te_counts[asset_attr.tvt_type] += 1

        # if use logging.info here, will cause error output when use mir show in linux pipe
        print(f"metadatas.mir: {len(mir_metadatas.attributes)} assets"
              f" (training: {un_tr_va_te_counts[mirpb.TvtTypeTraining]},"
              f" validation: {un_tr_va_te_counts[mirpb.TvtTypeValidation]},"
              f" test: {un_tr_va_te_counts[mirpb.TvtTypeTest]},"
              f" others: {un_tr_va_te_counts[mirpb.TvtTypeUnknown]})")

    @classmethod
    def _show_general_annotations(cls, mir_annotations: mirpb.MirAnnotations) -> None:
        print(
            f"    pred: {len(mir_annotations.prediction.image_annotations)}, "
            f"type: {mir_annotations.prediction.type}, "
            f"is instance segmentation: {mir_annotations.prediction.is_instance_segmentation}, "
            f"    gt: {len(mir_annotations.ground_truth.image_annotations)}, "
            f"type: {mir_annotations.ground_truth.type}, "
            f"is instance segmentation: {mir_annotations.ground_truth.is_instance_segmentation}")

    @classmethod
    def _show_general_context(cls, mir_context: mirpb.MirContext, mir_keywords: mirpb.MirKeywords) -> None:
        print(f"    main ck count: {len(mir_keywords.ck_idx)}")
        print(f"    gt tag count: {len(mir_keywords.gt_idx.tags)}")
        print(f"    pred tag count: {len(mir_keywords.pred_idx.tags)}")

    @classmethod
    def _show_general_tasks(cls, mir_tasks: mirpb.MirTasks, verbose: bool) -> None:
        hid = mir_tasks.head_task_id
        task = mir_tasks.tasks[hid]
        if not verbose:
            print(f"tasks.mir: hid: {hid}, code: {task.return_code}, error msg: {task.return_msg}\n"
                  f"    model hash: {task.model.model_hash}\n"
                  f"    map: {task.model.mAP}\n"
                  f"    executor: {task.executor}\n"
                  f"    stages: {list(task.model.stages.keys())}\n"
                  f"    best stage name: {task.model.best_stage_name}")
        else:
            print(f"tasks.mir: {json_format.MessageToDict(mir_tasks, preserving_proto_field_name=True)}")


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    show_arg_parser = subparsers.add_parser('show',
                                            parents=[parent_parser],
                                            description='use this command to show current workspace informations',
                                            help='show current workspace informations')
    show_arg_parser.add_argument('--verbose', dest='verbose', action='store_true', help='show verbose info')
    show_arg_parser.add_argument('--src-revs',
                                 dest='src_revs',
                                 type=str,
                                 default='HEAD',
                                 help='rev@bid: source rev and base task id')
    show_arg_parser.set_defaults(func=CmdShow)
