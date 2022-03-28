import argparse
import logging
from typing import Any, List

from google.protobuf import json_format

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, context, mir_storage, mir_storage_ops, revs_parser
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
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if check_code != MirCode.RC_OK:
            return check_code

        # show infos
        cls._show_cis(mir_root, src_typ_rev_tid, verbose)
        cls._show_cks(mir_root, src_typ_rev_tid, verbose)
        cls._show_general(mir_root, src_typ_rev_tid, verbose)

        return MirCode.RC_OK

    @classmethod
    def _show_general(cls, mir_root: str, src_typ_rev_tid: revs_parser.TypRevTid, verbose: bool) -> None:
        cls._show_general_context_config(mir_root=mir_root)

        [metadatas, annotations, _, tasks,
         context] = mir_storage_ops.MirStorageOps.load_multiple_storages(mir_root=mir_root,
                                                                         mir_branch=src_typ_rev_tid.rev,
                                                                         mir_task_id=src_typ_rev_tid.tid,
                                                                         ms_list=mir_storage.get_all_mir_storage(),
                                                                         as_dict=False)
        cls._show_general_metadatas(metadatas)
        cls._show_general_annotations(annotations)
        cls._show_general_context(context)
        cls._show_general_tasks(tasks, verbose)

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
        hid = mir_annotations.head_task_id
        print(f"annotations.mir: hid: {hid}," f" {len(mir_annotations.task_annotations[hid].image_annotations)} assets")

    @classmethod
    def _show_general_context(cls, mir_context: mirpb.MirContext) -> None:
        print(f"context.mir: negative assets cnt: {mir_context.negative_images_cnt}")
        print(f"    project negative assets cnt: {mir_context.project_negative_images_cnt}")
        print(f"    total assets cnt: {mir_context.images_cnt}")

    @classmethod
    def _show_general_context_config(cls, mir_root: str) -> None:
        project_class_ids = context.load(mir_root=mir_root)
        if project_class_ids:
            class_id_and_names: List[str] = []
            class_ids_mgr = class_ids.ClassIdManager(mir_root=mir_root)
            for class_id in project_class_ids:
                class_id_and_names.append(f"{class_id} ({class_ids_mgr.main_name_for_id(class_id)})")
            print(f"project classes: {'; '.join(class_id_and_names)}")
        else:
            print('project classes: none')

    @classmethod
    def _show_general_tasks(cls, mir_tasks: mirpb.MirTasks, verbose: bool) -> None:
        hid = mir_tasks.head_task_id
        task = mir_tasks.tasks[hid]
        if not verbose:
            print(f"tasks.mir: hid: {hid}, code: {task.return_code}, error msg: {task.return_msg}\n"
                  f"    model hash: {task.model.model_hash}\n"
                  f"    map: {task.model.mean_average_precision}\n"
                  f"    executor: {task.executor}")
        else:
            print(f"tasks.mir: {json_format.MessageToDict(mir_tasks, preserving_proto_field_name=True)}")

    @classmethod
    def _show_cis(cls, mir_root: str, src_typ_rev_tid: revs_parser.TypRevTid, verbose: bool) -> None:
        mir_context: mirpb.MirContext = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=mir_root, mir_branch=src_typ_rev_tid.rev, mir_task_id=src_typ_rev_tid.tid, ms=mirpb.MIR_CONTEXT)
        cls_id_mgr = class_ids.ClassIdManager(mir_root=mir_root)
        if verbose:
            print('predefined key ids and assets count:')
            cls._show_cis_verbose(predefined_keyids_cnt=mir_context.predefined_keyids_cnt, cls_id_mgr=cls_id_mgr)
            if mir_context.project_predefined_keyids_cnt:
                print('project predefined key ids and assets count:')
                cls._show_cis_verbose(predefined_keyids_cnt=mir_context.project_predefined_keyids_cnt,
                                      cls_id_mgr=cls_id_mgr)
        else:
            type_names = [cls_id_mgr.main_name_for_id(ci) or '' for ci in mir_context.predefined_keyids_cnt.keys()]
            print(';'.join(type_names))

    @classmethod
    def _show_cis_verbose(cls, predefined_keyids_cnt: Any, cls_id_mgr: class_ids.ClassIdManager) -> None:
        for ci, cnt in predefined_keyids_cnt.items():
            main_name = cls_id_mgr.main_name_for_id(ci)
            if main_name:
                print(f"  {main_name}: {cnt}")
            else:
                print(f"  {ci} (unknown ci): {cnt}")

    @classmethod
    def _show_cks(cls, mir_root: str, src_typ_rev_tid: revs_parser.TypRevTid, verbose: bool) -> None:
        print('')  # currently no customized keywords


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    show_arg_parser = subparsers.add_parser('show',
                                            parents=[parent_parser],
                                            description='use this command to show current workspace informations',
                                            help='show current workspace informations')
    show_arg_parser.add_argument('--verbose', dest='verbose', action='store_true', help='show verbose info')
    show_arg_parser.add_argument('--src-revs', dest='src_revs', type=str, help='rev@bid: source rev and base task id')
    show_arg_parser.set_defaults(func=CmdShow)
