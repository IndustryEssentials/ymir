"""
mir merge: merge contents from another guest branch to current branch
"""

import argparse
import datetime
import logging
from typing import Any, Mapping, Tuple

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, mir_storage, mir_storage_ops, revs_parser
from mir.tools.code import MirCode


def _match_asset_ids(host_ids: set, guest_ids: set) -> Tuple[set, set, set]:
    """
    match asset ids

    Args:
        host_ids (set): host ids
        guest_ids (set): guest ids

    Returns:
        Tuple[set, set, set]: host_only_ids, guest_only_ids, joint_ids
    """
    insets = host_ids & guest_ids
    return (host_ids - insets, guest_ids - insets, insets)


def _merge_metadatas(host_mir_metadatas: mirpb.MirMetadatas, guest_mir_metadatas: mirpb.MirMetadatas,
                     id_guest_only: set, id_joint: set, suggested_tvt_type: 'mirpb.TvtType.V', strategy: str) -> None:
    if not host_mir_metadatas or not guest_mir_metadatas:
        raise ValueError("input host/guest mir_metadatas is invalid")

    # for all ids only in `guest_mir_metadatas`, add them to `host_mir_metadatas`
    for asset_id in id_guest_only:
        host_mir_metadatas.attributes[asset_id].CopyFrom(guest_mir_metadatas.attributes[asset_id])
        if suggested_tvt_type != mirpb.TvtTypeUnknown:
            host_mir_metadatas.attributes[asset_id].tvt_type = suggested_tvt_type
    # for all ids in both two mir_metadatas
    if strategy == "guest":
        for asset_id in id_joint:
            host_mir_metadatas.attributes[asset_id].CopyFrom(guest_mir_metadatas.attributes[asset_id])
            if suggested_tvt_type != mirpb.TvtTypeUnknown:
                host_mir_metadatas.attributes[asset_id].tvt_type = suggested_tvt_type
    elif strategy == "host":
        pass
    elif strategy == "stop":
        if len(id_joint) > 0:
            raise RuntimeError("joint ids detected, stop")
    else:
        raise ValueError("invalid strategy")


# WARNING: annotations are filtered in task level, NOT in image level.
def _merge_annotations(host_mir_annotations: mirpb.MirAnnotations, guest_mir_annotations: mirpb.MirAnnotations,
                       strategy: str) -> None:
    """
    add all annotations in guest_mir_annotations into host_mir_annotations

    Args:
        host_mir_annotations (mirpb.MirAnnotations): host annotations
        guest_mir_annotations (mirpb.MirAnnotations): guest annotations
        strategy (str): host, guest, stop

    Raises:
        ValueError: if host or guest annotations empty
        ValueError: if conflicts occured in strategy stop
    """
    if not host_mir_annotations or not guest_mir_annotations:
        raise ValueError("input host/guest mir_annotations is invalid")
    if not host_mir_annotations.head_task_id:
        raise ValueError("no head_task_id found in host_mir_annotations")
    if len(guest_mir_annotations.task_annotations) == 0:
        logging.warning('empty guest_mir_annotations')
        return

    task_id = host_mir_annotations.head_task_id
    host_image_annotations = host_mir_annotations.task_annotations[host_mir_annotations.head_task_id].image_annotations
    guest_image_annotations = guest_mir_annotations.task_annotations[
        guest_mir_annotations.head_task_id].image_annotations
    host_only_ids, guest_only_ids, joint_ids = _match_asset_ids(set(host_image_annotations.keys()),
                                                                set(guest_image_annotations.keys()))

    if strategy == "stop" and joint_ids:
        raise ValueError("found conflicts; abort")

    for asset_id in host_only_ids:
        host_mir_annotations.task_annotations[task_id].image_annotations[asset_id].CopyFrom(
            host_image_annotations[asset_id])
    for asset_id in guest_only_ids:
        host_mir_annotations.task_annotations[task_id].image_annotations[asset_id].CopyFrom(
            guest_image_annotations[asset_id])
    for asset_id in joint_ids:
        if strategy.lower() == "host":
            if asset_id not in host_mir_annotations.task_annotations[task_id].image_annotations:
                host_mir_annotations.task_annotations[task_id].image_annotations[asset_id].CopyFrom(
                    host_image_annotations[asset_id])
        elif strategy.lower() == "guest":
            host_mir_annotations.task_annotations[task_id].image_annotations[asset_id].CopyFrom(
                guest_image_annotations[asset_id])


def _get_union_keywords(host_keywords: Any, guest_keywords: Any, strategy: str) -> set:
    if host_keywords:
        host_keywords_set = set(host_keywords)
    else:
        host_keywords_set = set()
    if guest_keywords:
        guest_keywords_set = set(guest_keywords)
    else:
        guest_keywords_set = set()

    if strategy == "host":
        merged_keywords_set = host_keywords_set
    elif strategy == "guest":
        merged_keywords_set = guest_keywords_set
    else:
        raise Exception("unknown strategy type: " + strategy)
    return merged_keywords_set


def _merge_keywords(host_mir_keywords: Mapping, guest_mir_keywords: Mapping, id_guest_only: set, id_joint: set,
                    strategy: str) -> None:
    if host_mir_keywords is None or guest_mir_keywords is None:
        raise RuntimeError('Invalid keywords message map.')

    for asset_id in id_guest_only:
        if asset_id not in guest_mir_keywords:
            continue
        host_mir_keywords[asset_id].predifined_keyids[:] = guest_mir_keywords[asset_id].predifined_keyids
        host_mir_keywords[asset_id].customized_keywords[:] = guest_mir_keywords[asset_id].customized_keywords

    for asset_id in id_joint:
        if asset_id not in guest_mir_keywords:
            continue

        merged_keywords_set_predifined = _get_union_keywords(host_mir_keywords[asset_id].predifined_keyids,
                                                             guest_mir_keywords[asset_id].predifined_keyids, strategy)

        if merged_keywords_set_predifined:
            host_mir_keywords[asset_id].predifined_keyids[:] = merged_keywords_set_predifined

        merged_keywords_set_customized = _get_union_keywords(host_mir_keywords[asset_id].customized_keywords,
                                                             guest_mir_keywords[asset_id].customized_keywords, strategy)

        if merged_keywords_set_customized:
            host_mir_keywords[asset_id].customized_keywords[:] = merged_keywords_set_customized


def _merge_tasks(host_mir_tasks: mirpb.MirTasks, guest_mir_tasks: mirpb.MirTasks) -> None:
    if not host_mir_tasks or not guest_mir_tasks:
        raise ValueError("input host/guest mir_tasks is invalid")

    for guest_task_id, guest_task in guest_mir_tasks.tasks.items():
        if guest_task_id not in host_mir_tasks.tasks:
            host_mir_tasks.tasks[guest_task_id].CopyFrom(guest_task)


def _tvt_type_from_str(typ: str) -> 'mirpb.TvtType.V':
    if typ == "tr":
        return mirpb.TvtTypeTraining
    elif typ == "va":
        return mirpb.TvtTypeValidation
    elif typ == "te":
        return mirpb.TvtTypeTest
    elif not typ:
        return mirpb.TvtTypeUnknown
    else:
        raise ValueError(f"invalid typ: {typ}")


def _merge_to_mir(host_mir_metadatas: mirpb.MirMetadatas, host_mir_annotations: mirpb.MirAnnotations,
                  host_mir_keywords: mirpb.MirKeywords, host_mir_tasks: mirpb.MirTasks, mir_root: str,
                  guest_typ_rev_tid: revs_parser.TypRevTid, strategy: str) -> int:
    """
    merge contents in `guest_typ_rev_tid` to `host_mir_xxx`

    Args:
        host_mir_metadatas (mirpb.MirMetadatas): host metadatas
        host_mir_annotations (mirpb.MirAnnotations): host annotations
        host_mir_keywords (mirpb.MirKeywords): host keywords
        host_mir_tasks (mirpb.MirTasks): host tasks
        mir_root (str): path to mir repo
        guest_typ_rev_tid (revs_parser.TypRevTid): guest typ:rev@tid
        strategy (str): host / guest / stop

    Raises:
        RuntimeError: when guest branch has no metadatas, or guest branch has no tasks
    """
    mir_data = mir_storage_ops.MirStorageOps.load(mir_root=mir_root,
                                                  mir_branch=guest_typ_rev_tid.rev,
                                                  mir_storages=mir_storage.get_all_mir_storage())

    guest_mir_metadatas: mirpb.MirMetadatas = mir_data.get(mirpb.MirStorage.MIR_METADATAS, None)
    if not guest_mir_metadatas:
        raise RuntimeError(f"guest repo {mir_root}:{guest_typ_rev_tid.rev} has no metadata.")

    id_host_only, id_guest_only, id_joint = _match_asset_ids(set(host_mir_metadatas.attributes.keys()),
                                                             set(guest_mir_metadatas.attributes.keys()))

    logging.info(f"{guest_typ_rev_tid} host assets: {len(id_host_only)}, guest assets: {len(id_guest_only)}, "
                 f"joint assets: {len(id_joint)}")

    # if no guest_only assets found, return
    if not id_guest_only and not id_joint:
        return MirCode.RC_OK
    if strategy.lower() == "stop" and id_joint:
        logging.warning("found conflict on merge strategy STOP: abort")
        return MirCode.RC_CMD_CONFLICTS_OCCURED

    _merge_metadatas(host_mir_metadatas=host_mir_metadatas,
                     guest_mir_metadatas=guest_mir_metadatas,
                     id_guest_only=id_guest_only,
                     id_joint=id_joint,
                     suggested_tvt_type=_tvt_type_from_str(guest_typ_rev_tid.typ),
                     strategy=strategy)

    guest_mir_annotations: mirpb.MirAnnotations = mir_data.get(mirpb.MirStorage.MIR_ANNOTATIONS, None)
    if not guest_mir_annotations:
        logging.warning("guest repo {}:{} has no annotations.".format(mir_root, guest_typ_rev_tid.rev))
    _merge_annotations(host_mir_annotations=host_mir_annotations,
                       guest_mir_annotations=guest_mir_annotations,
                       strategy=strategy)

    guest_mir_keywords: mirpb.MirKeywords = mir_data.get(mirpb.MirStorage.MIR_KEYWORDS, None)
    if not guest_mir_keywords:
        logging.warning(f"guest repo {mir_root}:{guest_typ_rev_tid.rev} has no keywords.")
    _merge_keywords(host_mir_keywords.keywords, guest_mir_keywords.keywords, id_guest_only, id_joint, strategy)

    guest_mir_tasks = mir_data.get(mirpb.MirStorage.MIR_TASKS, None)
    if not guest_mir_tasks:
        raise RuntimeError(f"guest repo {mir_root}:{guest_typ_rev_tid.rev} has no tasks.")
    _merge_tasks(host_mir_tasks, guest_mir_tasks)

    return MirCode.RC_OK


def _exclude_from_mir(host_mir_metadatas: mirpb.MirMetadatas, host_mir_annotations: mirpb.MirAnnotations,
                      host_mir_keywords: mirpb.MirKeywords, mir_root: str, branch_id: str) -> int:
    if not branch_id:
        raise RuntimeError('empty exclude id')
    if not host_mir_metadatas:
        raise RuntimeError('invalid host_mir_metadatas')

    guest_mir_metadatas: mirpb.MirMetadatas = mir_storage_ops.MirStorageOps.load_single(
        mir_root=mir_root, mir_branch=branch_id, ms=mirpb.MirStorage.MIR_METADATAS)
    if not guest_mir_metadatas:
        raise RuntimeError("guest repo {}:{} has no metadata.".format(mir_root, branch_id))

    _, _, id_joint = _match_asset_ids(set(host_mir_metadatas.attributes.keys()),
                                      set(guest_mir_metadatas.attributes.keys()))
    for asset_id in id_joint:
        del host_mir_metadatas.attributes[asset_id]

        if asset_id in host_mir_annotations.task_annotations[host_mir_annotations.head_task_id].image_annotations:
            del host_mir_annotations.task_annotations[host_mir_annotations.head_task_id].image_annotations[asset_id]
        if asset_id in host_mir_keywords.keywords:
            del host_mir_keywords.keywords[asset_id]
    return MirCode.RC_OK


class CmdMerge(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command merge: %s", self.args)
        return CmdMerge.run_with_args(mir_root=self.args.mir_root,
                                      src_revs=self.args.src_revs,
                                      ex_src_revs=self.args.ex_src_revs,
                                      dst_rev=self.args.dst_rev,
                                      strategy=self.args.strategy)

    @staticmethod
    def run_with_args(mir_root: str, src_revs: str, ex_src_revs: str, dst_rev: str, strategy: str) -> int:
        if not src_revs or not dst_rev:
            logging.error("empty --src-revs or --dst-rev")
            return MirCode.RC_CMD_INVALID_ARGS
        src_typ_rev_tids = revs_parser.parse_arg_revs(src_revs)
        if checker.check_src_revs(src_typ_rev_tids) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)
        if checker.check_dst_rev(dst_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS

        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        # Read host id mir data.
        host_mir_metadatas = mirpb.MirMetadatas()
        host_mir_annotations = mirpb.MirAnnotations()
        host_mir_keywords = mirpb.MirKeywords()
        host_mir_tasks = mirpb.MirTasks()

        host_mir_annotations.head_task_id = dst_typ_rev_tid.tid

        for typ_rev_tid in src_typ_rev_tids:
            ret = _merge_to_mir(host_mir_metadatas=host_mir_metadatas,
                                host_mir_annotations=host_mir_annotations,
                                host_mir_keywords=host_mir_keywords,
                                host_mir_tasks=host_mir_tasks,
                                mir_root=mir_root,
                                guest_typ_rev_tid=typ_rev_tid,
                                strategy=strategy)
            if ret != MirCode.RC_OK:
                return ret

        ex_typ_rev_tids = revs_parser.parse_arg_revs(ex_src_revs)
        for typ_rev_tid in ex_typ_rev_tids:
            if checker.check_src_revs(typ_rev_tid) != MirCode.RC_OK:
                return MirCode.RC_CMD_INVALID_ARGS

            ret = _exclude_from_mir(host_mir_metadatas=host_mir_metadatas,
                                    host_mir_annotations=host_mir_annotations,
                                    host_mir_keywords=host_mir_keywords,
                                    mir_root=mir_root,
                                    branch_id=typ_rev_tid.rev)

            if ret != MirCode.RC_OK:
                return ret

        # create and write tasks
        task = mirpb.Task()
        task.type = mirpb.TaskTypeMerge
        task.name = f"merge: {src_revs} - {ex_src_revs} to {dst_rev}"
        task.task_id = dst_typ_rev_tid.tid
        task.timestamp = int(datetime.datetime.now().timestamp())
        mir_storage_ops.add_mir_task(host_mir_tasks, task)

        host_typ_rev_tid = src_typ_rev_tids[0]
        mir_data = {
            mirpb.MirStorage.MIR_METADATAS: host_mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: host_mir_annotations,
            mirpb.MirStorage.MIR_TASKS: host_mir_tasks,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=host_typ_rev_tid.rev,
                                                      mir_datas=mir_data,
                                                      commit_message=task.name)

        logging.debug("mir merge: write files done")

        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    merge_arg_parser = subparsers.add_parser("merge",
                                             parents=[parent_parser],
                                             description="use this command to merge contents from other branch",
                                             help="merge contents from other branch")
    merge_arg_parser.add_argument("--src-revs",
                                  dest="src_revs",
                                  type=str,
                                  required=True,
                                  help="source tvt types, revs and base task ids, first the host, others the guests, "
                                  "can begin with tr:/va:/te:, uses own tvt type if no prefix assigned")
    merge_arg_parser.add_argument("--ex-src-revs",
                                  dest="ex_src_revs",
                                  type=str,
                                  help="branch(es) id, from which you want to exclude, seperated by comma.")
    merge_arg_parser.add_argument("--dst-rev",
                                  dest="dst_rev",
                                  type=str,
                                  required=True,
                                  help="rev@tid: destination branch name and task id")
    merge_arg_parser.add_argument("-s",
                                  dest="strategy",
                                  type=str,
                                  default="stop",
                                  choices=["stop", "host", "guest"],
                                  help="conflict resolvation strategy, stop (default): stop when conflict detects; "
                                  "host: use host; guest: use guest")
    merge_arg_parser.set_defaults(func=CmdMerge)
