import argparse
import logging

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, mir_storage, mir_storage_ops, revs_parser
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
        if not src_revs:
            logging.error('invalid args: empty --src-revs, abort')
            return MirCode.RC_CMD_INVALID_ARGS
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
        if checker.check_src_revs(src_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS
        check_code = checker.check(mir_root,
                                   [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if check_code != MirCode.RC_OK:
            return check_code

        # show infos
        cls._show_cis(mir_root, src_typ_rev_tid, verbose)
        cls._show_cks(mir_root, src_typ_rev_tid, verbose)
        cls._show_general(mir_root, src_typ_rev_tid)

        return MirCode.RC_OK

    @classmethod
    def _show_general(cls, mir_root: str, src_typ_rev_tid: revs_parser.TypRevTid) -> None:
        mir_datas = mir_storage_ops.MirStorageOps.load(mir_root=mir_root,
                                                       mir_branch=src_typ_rev_tid.rev,
                                                       mir_task_id=src_typ_rev_tid.tid,
                                                       mir_storages=mir_storage.get_all_mir_storage())

        mir_metadatas: mirpb.MirMetadatas = mir_datas.get(mirpb.MirStorage.MIR_METADATAS, None)
        if mir_metadatas:
            cls._show_general_metadatas(mir_metadatas)
        mir_annotations: mirpb.MirAnnotations = mir_datas.get(mirpb.MirStorage.MIR_ANNOTATIONS, None)
        if mir_annotations:
            cls._show_general_annotations(mir_annotations)
        mir_tasks: mirpb.MirTasks = mir_datas.get(mirpb.MIR_TASKS, None)
        if mir_tasks:
            cls._show_general_tasks(mir_tasks)

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
    def _show_general_tasks(cls, mir_tasks: mirpb.MirTasks) -> None:
        hid = mir_tasks.head_task_id
        task = mir_tasks.tasks[hid]
        print(f"tasks.mir: hid: {hid}, code: {task.return_code}, error msg: {task.return_msg}\n"
              f"    model hash: {task.model.model_hash}, map: {task.model.mean_average_precision}")

    @classmethod
    def _show_cis(cls, mir_root: str, src_typ_rev_tid: revs_parser.TypRevTid, verbose: bool) -> None:
        mir_keywords: mirpb.MirKeywords = mir_storage_ops.MirStorageOps.load_single(mir_root=mir_root,
                                                                                    mir_branch=src_typ_rev_tid.rev,
                                                                                    mir_task_id=src_typ_rev_tid.tid,
                                                                                    ms=mirpb.MIR_KEYWORDS)
        cls_id_mgr = class_ids.ClassIdManager(mir_root=mir_root)
        if verbose:
            print(f"predefined key ids ({len(mir_keywords.predifined_keyids_cnt)}):")
            for ci, cnt in mir_keywords.predifined_keyids_cnt.items():
                main_name = cls_id_mgr.main_name_for_id(ci)
                if main_name:
                    print(f"  {main_name}: {cnt}")
                else:
                    print(f"  {ci} (unknown ci): {cnt}")
        else:
            type_names = [cls_id_mgr.main_name_for_id(ci) or '' for ci in mir_keywords.predifined_keyids_cnt.keys()]
            print(';'.join(type_names))

    @classmethod
    def _show_cks(cls, mir_root: str, src_typ_rev_tid: revs_parser.TypRevTid, verbose: bool) -> None:
        mir_keywords: mirpb.MirKeywords = mir_storage_ops.MirStorageOps.load_single(mir_root=mir_root,
                                                                                    mir_branch=src_typ_rev_tid.rev,
                                                                                    mir_task_id=src_typ_rev_tid.tid,
                                                                                    ms=mirpb.MIR_KEYWORDS)
        if verbose:
            print(f"customized keywords ({len(mir_keywords.customized_keywords_cnt)}):")
            for ck, cnt in mir_keywords.customized_keywords_cnt.items():
                print(f"  {ck}: {cnt}")
        else:
            cks = list(mir_keywords.customized_keywords_cnt.keys())
            print(';'.join(cks))


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    show_arg_parser = subparsers.add_parser('show',
                                            parents=[parent_parser],
                                            description='use this command to show current workspace informations',
                                            help='show current workspace informations')
    show_arg_parser.add_argument('--verbose', dest='verbose', action='store_true', help='show verbose info')
    show_arg_parser.add_argument('--src-revs', dest='src_revs', type=str, help='rev@bid: source rev and base task id')
    show_arg_parser.set_defaults(func=CmdShow)
