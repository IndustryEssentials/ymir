import argparse
import logging
from typing import Any, Callable, List, Tuple, Optional, Set, Union

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, class_ids, mir_repo_utils, mir_storage, mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter

# type for function `__include_match` and `__exclude_match`
__IncludeExcludeCallableType = Callable[[Set[str], mirpb.MirKeywords, str, Any], Set[str]]


class CmdFilter(base.BaseCommand):
    # private: misc
    @staticmethod
    def __preds_set_from_str(preds_str: str, cls_mgr: class_ids.ClassIdManager) -> Set[int]:
        if not preds_str:
            return set()

        class_names = preds_str.split(";")
        class_ids, unknown_names = cls_mgr.id_for_names(class_names)
        if unknown_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"unknwon class names: {unknown_names}")

        return set(class_ids)

    @staticmethod
    def __include_match(asset_ids_set: Set[str], mir_keywords: mirpb.MirKeywords, attr_name: str,
                        in_set: Set[Union[int, str]]) -> Set[str]:
        # if don't need include match, returns all
        if not in_set:
            return asset_ids_set

        matched_asset_ids_set = set()  # type: Set[str]
        for asset_id in asset_ids_set:
            if asset_id not in mir_keywords.keywords:
                continue

            keyids_set = set(getattr(mir_keywords.keywords[asset_id], attr_name))
            if not keyids_set:
                continue

            if keyids_set & in_set:
                matched_asset_ids_set.add(asset_id)
        return matched_asset_ids_set

    @staticmethod
    def __exclude_match(asset_ids_set: Set[str], mir_keywords: mirpb.MirKeywords, attr_name: str,
                        ex_set: Set[Union[int, str]]) -> Set[str]:
        # if don't need excludes filter, returns all
        if not ex_set:
            return asset_ids_set

        matched_asset_ids_set = set()  # type: Set[str]
        for asset_id in asset_ids_set:
            if asset_id in mir_keywords.keywords:
                keyids_set = set(getattr(mir_keywords.keywords[asset_id], attr_name))
                if keyids_set & ex_set:
                    continue
            matched_asset_ids_set.add(asset_id)
        return matched_asset_ids_set

    # public: run cmd
    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, in_cis: Optional[str], ex_cis: Optional[str], in_cks: Optional[str],
                      ex_cks: Optional[str], src_revs: str, dst_rev: str, work_dir: str) -> int:  # type: ignore
        # check args
        in_cis = in_cis.strip().lower() if in_cis else ''
        ex_cis = ex_cis.strip().lower() if ex_cis else ''
        in_cks = in_cks.strip() if in_cks else ''
        ex_cks = ex_cks.strip() if ex_cks else ''

        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        PhaseLoggerCenter.create_phase_loggers(top_phase='filter',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name=dst_typ_rev_tid.tid)

        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if return_code != MirCode.RC_OK:
            return return_code

        [mir_metadatas, mir_annotations, mir_keywords, mir_tasks,
         _] = mir_storage_ops.MirStorageOps.load_multiple_storages(mir_root=mir_root,
                                                                   mir_branch=src_typ_rev_tid.rev,
                                                                   mir_task_id=src_typ_rev_tid.tid,
                                                                   ms_list=mir_storage.get_all_mir_storage(),
                                                                   as_dict=False)
        task_id = dst_typ_rev_tid.tid
        base_task_id = mir_annotations.head_task_id

        PhaseLoggerCenter.update_phase(phase='filter.read')

        if task_id in mir_tasks.tasks:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_BRANCH_OR_TAG,
                                  error_message=f"invalid args: task id already exists: {task_id}")
        if not base_task_id:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                                  error_message='no base task id in tasks.mir')

        assert len(mir_annotations.task_annotations.keys()) == 1
        base_task_annotations = mir_annotations.task_annotations[base_task_id]  # type: mirpb.SingleTaskAnnotations

        class_manager = class_ids.ClassIdManager(mir_root=mir_root)
        preds_set = CmdFilter.__preds_set_from_str(in_cis, class_manager)  # type: Set[int]
        excludes_set = CmdFilter.__preds_set_from_str(ex_cis, class_manager)  # type: Set[int]
        ck_preds_set = {ck.strip() for ck in in_cks.split(";")} if in_cks else set()
        ck_excludes_set = {ck.strip() for ck in ex_cks.split(";")} if ex_cks else set()

        asset_ids_set = set(mir_metadatas.attributes.keys())
        match_functions: List[Tuple[__IncludeExcludeCallableType, Union[Set[str], Set[int]], str, str]] = [
            (CmdFilter.__include_match, preds_set, 'predifined_keyids', 'select cis'),
            (CmdFilter.__exclude_match, excludes_set, 'predifined_keyids', 'exclude cis'),
            (CmdFilter.__include_match, ck_preds_set, 'customized_keywords', 'select cks'),
            (CmdFilter.__exclude_match, ck_excludes_set, 'customized_keywords', 'exclude cks')
        ]
        for match_func, ci_ck_conditions, attr_name, message in match_functions:
            if ci_ck_conditions:
                logging.info(f"assets count before {message}: {len(asset_ids_set)}")
                asset_ids_set = match_func(asset_ids_set, mir_keywords, attr_name, ci_ck_conditions)
                logging.info(f"assets count after {message}: {len(asset_ids_set)}")

        matched_mir_metadatas = mirpb.MirMetadatas()
        matched_mir_annotations = mirpb.MirAnnotations()
        matched_mir_keywords = mirpb.MirKeywords()

        # generate matched metadatas, annotations and keywords
        for asset_id in asset_ids_set:
            # generate `matched_mir_metadatas`
            asset_attr = mir_metadatas.attributes[asset_id]
            matched_mir_metadatas.attributes[asset_id].CopyFrom(asset_attr)

        joint_ids = asset_ids_set & mir_keywords.keywords.keys()
        for asset_id in joint_ids:
            # generate `matched_mir_keywords`
            matched_mir_keywords.keywords[asset_id].CopyFrom(mir_keywords.keywords[asset_id])

        # generate `matched_mir_annotations`
        joint_ids = asset_ids_set & base_task_annotations.image_annotations.keys()
        for asset_id in joint_ids:
            matched_mir_annotations.task_annotations[task_id].image_annotations[asset_id].CopyFrom(
                base_task_annotations.image_annotations[asset_id])

        logging.info("matched: %d, overriding current mir repo", len(matched_mir_metadatas.attributes))

        PhaseLoggerCenter.update_phase(phase='filter.change')

        commit_message = f"filter select: {in_cis} exclude: {ex_cis}"
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeFilter,
                                           task_id=task_id,
                                           message=commit_message,
                                           src_revs=src_revs,
                                           dst_rev=dst_rev)
        matched_mir_contents = {
            mirpb.MirStorage.MIR_METADATAS: matched_mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: matched_mir_annotations,
        }

        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=src_typ_rev_tid.rev,
                                                      mir_datas=matched_mir_contents,
                                                      task=task)

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command filter: %s", self.args)
        return CmdFilter.run_with_args(mir_root=self.args.mir_root,
                                       in_cis=self.args.in_cis,
                                       ex_cis=self.args.ex_cis,
                                       in_cks=self.args.in_cks,
                                       ex_cks=self.args.ex_cks,
                                       src_revs=self.args.src_revs,
                                       dst_rev=self.args.dst_rev,
                                       work_dir=self.args.work_dir)


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    filter_arg_parser = subparsers.add_parser("filter",
                                              parents=[parent_parser],
                                              description="use this command to filter assets",
                                              help="filter assets")
    filter_arg_parser.add_argument("-p", dest="in_cis", type=str, help="type names")
    filter_arg_parser.add_argument("-P", dest="ex_cis", type=str, help="exclusive type names")
    filter_arg_parser.add_argument("-c", dest="in_cks", type=str, help="customized keywords")
    filter_arg_parser.add_argument("-C", dest="ex_cks", type=str, help="excludsive customized keywords")
    filter_arg_parser.add_argument("--src-revs", dest="src_revs", type=str, help="type:rev@bid")
    filter_arg_parser.add_argument("--dst-rev", dest="dst_rev", type=str, help="rev@tid")
    filter_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    filter_arg_parser.set_defaults(func=CmdFilter)
