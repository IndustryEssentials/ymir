import argparse
import logging
from typing import Optional, Set

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import annotations, checker, class_ids
from mir.tools import mir_repo_utils, mir_storage, mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter


class CmdFilter(base.BaseCommand):
    # private: misc
    @staticmethod
    def __class_ids_set_from_str(preds_str: str, cls_mgr: class_ids.UserLabels) -> Set[int]:
        if not preds_str:
            return set()

        class_names = preds_str.split(";")
        class_ids, unknown_names = cls_mgr.id_for_names(class_names)
        if unknown_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"unknwon class names: {unknown_names}")

        return set(class_ids)

    @classmethod
    def __include_match(cls, asset_ids_set: Set[str], mir_keywords: mirpb.MirKeywords,
                        in_cis_set: Set[int]) -> Set[str]:
        # if don't need include match, returns all
        if not in_cis_set:
            return asset_ids_set

        asset_ids_set = set()
        for ci in in_cis_set:
            if ci in mir_keywords.pred_idx.cis:
                asset_ids_set.update(mir_keywords.pred_idx.cis[ci].key_ids.keys())
            if ci in mir_keywords.gt_idx.cis:
                asset_ids_set.update(mir_keywords.gt_idx.cis[ci].key_ids.keys())
        return asset_ids_set

    @classmethod
    def __exclude_match(cls, asset_ids_set: Set[str], mir_keywords: mirpb.MirKeywords,
                        ex_cis_set: Set[int]) -> Set[str]:
        if not ex_cis_set:
            return asset_ids_set

        for ci in ex_cis_set:
            if ci in mir_keywords.pred_idx.cis:
                asset_ids_set.difference_update(mir_keywords.pred_idx.cis[ci].key_ids.keys())
            if ci in mir_keywords.gt_idx.cis:
                asset_ids_set.difference_update(mir_keywords.gt_idx.cis[ci].key_ids.keys())
        return asset_ids_set

    @staticmethod
    def __gen_task_annotations(src_task_annotations: mirpb.SingleTaskAnnotations,
                               dst_task_annotations: mirpb.SingleTaskAnnotations, asset_ids: Set[str]) -> None:
        joint_ids = asset_ids & src_task_annotations.image_annotations.keys()
        for asset_id in joint_ids:
            dst_task_annotations.image_annotations[asset_id].CopyFrom(src_task_annotations.image_annotations[asset_id])

    # public: run cmd
    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, in_cis: Optional[str], ex_cis: Optional[str], src_revs: str, dst_rev: str,
                      work_dir: str) -> int:  # type: ignore
        # check args
        in_cis = in_cis.strip().lower() if in_cis else ''
        ex_cis = ex_cis.strip().lower() if ex_cis else ''

        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        PhaseLoggerCenter.create_phase_loggers(top_phase='filter',
                                               monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir),
                                               task_name=dst_typ_rev_tid.tid)

        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.HAVE_LABELS])
        if return_code != MirCode.RC_OK:
            return return_code

        PhaseLoggerCenter.update_phase(phase="filter.init")

        [mir_metadatas, mir_annotations, mir_keywords, mir_tasks,
         _] = mir_storage_ops.MirStorageOps.load_multiple_storages(mir_root=mir_root,
                                                                   mir_branch=src_typ_rev_tid.rev,
                                                                   mir_task_id=src_typ_rev_tid.tid,
                                                                   ms_list=mir_storage.get_all_mir_storage(),
                                                                   as_dict=False)
        task_id = dst_typ_rev_tid.tid

        PhaseLoggerCenter.update_phase(phase='filter.read')

        class_manager = class_ids.load_or_create_userlabels(mir_root=mir_root)
        in_cis_set: Set[int] = CmdFilter.__class_ids_set_from_str(in_cis, class_manager)
        ex_cis_set: Set[int] = CmdFilter.__class_ids_set_from_str(ex_cis, class_manager)

        asset_ids_set = set(mir_metadatas.attributes.keys())
        asset_ids_set = CmdFilter.__include_match(asset_ids_set=asset_ids_set,
                                                  mir_keywords=mir_keywords,
                                                  in_cis_set=in_cis_set)
        logging.info(f"assets count after include match: {len(asset_ids_set)}")
        asset_ids_set = CmdFilter.__exclude_match(asset_ids_set=asset_ids_set,
                                                  mir_keywords=mir_keywords,
                                                  ex_cis_set=ex_cis_set)
        logging.info(f"assets count after exclude match: {len(asset_ids_set)}")

        matched_mir_metadatas = mirpb.MirMetadatas()
        matched_mir_annotations = mirpb.MirAnnotations()

        # generate matched metadatas, annotations and keywords
        for asset_id in asset_ids_set:
            # generate `matched_mir_metadatas`
            asset_attr = mir_metadatas.attributes[asset_id]
            matched_mir_metadatas.attributes[asset_id].CopyFrom(asset_attr)

        # generate `matched_mir_annotations`
        CmdFilter.__gen_task_annotations(src_task_annotations=mir_annotations.ground_truth,
                                         dst_task_annotations=matched_mir_annotations.ground_truth,
                                         asset_ids=asset_ids_set)
        CmdFilter.__gen_task_annotations(src_task_annotations=mir_annotations.prediction,
                                         dst_task_annotations=matched_mir_annotations.prediction,
                                         asset_ids=asset_ids_set)

        image_ck_asset_ids = asset_ids_set & set(mir_annotations.image_cks.keys())
        for asset_id in image_ck_asset_ids:
            matched_mir_annotations.image_cks[asset_id].CopyFrom(mir_annotations.image_cks[asset_id])

        annotations.copy_annotations_pred_meta(src_task_annotations=mir_annotations.prediction,
                                               dst_task_annotations=matched_mir_annotations.prediction)

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
                                       src_revs=self.args.src_revs,
                                       dst_rev=self.args.dst_rev,
                                       work_dir=self.args.work_dir)


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    filter_arg_parser = subparsers.add_parser("filter",
                                              parents=[parent_parser],
                                              description="use this command to filter assets",
                                              help="filter assets")
    filter_arg_parser.add_argument("-p", '--cis', dest="in_cis", type=str, help="type names")
    filter_arg_parser.add_argument("-P", '--ex-cis', dest="ex_cis", type=str, help="exclusive type names")
    filter_arg_parser.add_argument("--src-revs", dest="src_revs", type=str, help="type:rev@bid")
    filter_arg_parser.add_argument("--dst-rev", dest="dst_rev", type=str, help="rev@tid")
    filter_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    filter_arg_parser.set_defaults(func=CmdFilter)
