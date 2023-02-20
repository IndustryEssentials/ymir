import argparse
import logging
import random

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops, revs_parser
from mir.tools.annotations import filter_mirdatas_by_asset_ids
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError


class CmdSampling(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command sampling: %s", self.args)
        return CmdSampling.run_with_args(mir_root=self.args.mir_root,
                                         work_dir=self.args.work_dir,
                                         src_revs=self.args.src_revs,
                                         dst_rev=self.args.dst_rev,
                                         count=self.args.count,
                                         rate=self.args.rate)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, work_dir: str, src_revs: str, dst_rev: str, count: int, rate: float) -> int:
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs, need_tid=False)
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev, need_tid=True)

        if not mir_root:
            mir_root = '.'

        # read all
        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_metadatas, mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=src_typ_rev_tid.rev,
            mir_task_id=src_typ_rev_tid.tid,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS],
            as_dict=False,
        )

        sample_with_pb(mir_metadatas=mir_metadatas,
                       mir_annotations=mir_annotations,
                       count=count,
                       rate=rate)

        logging.info(f"sampling done, assets count: {len(mir_metadatas.attributes)}")

        # commit
        message = f"sampling src: {src_revs}, dst: {dst_rev}, count: {count}, rate: {rate}"
        task = mir_storage_ops.create_task_record(task_type=mirpb.TaskType.TaskTypeSampling,
                                                  task_id=dst_typ_rev_tid.tid,
                                                  message=message,
                                                  src_revs=src_revs,
                                                  dst_rev=dst_rev)

        # save and commit
        sampled_mir_datas = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_typ_rev_tid.rev,
                                                      his_branch=src_typ_rev_tid.rev,
                                                      mir_datas=sampled_mir_datas,
                                                      task=task)

        return MirCode.RC_OK


def sample_with_pb(mir_metadatas: mirpb.MirMetadatas, mir_annotations: mirpb.MirAnnotations, count: int,
                   rate: float) -> None:
    if count == 0 and (rate == 0 or rate >= 1.0 - 1e-9):
        return
    if count < 0 or rate < 0 or rate > 1:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid args: count or rate')

    assets_count = len(mir_metadatas.attributes)
    sampled_assets_count = 0
    if count > 0:
        sampled_assets_count = count
    else:
        sampled_assets_count = int(assets_count * rate)
    if sampled_assets_count < 0:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"sampled assets count: {sampled_assets_count} is negative")
    if sampled_assets_count > assets_count:
        logging.warning(f"sampled assets count: {sampled_assets_count} > assets count: {assets_count}, select all")
        sampled_assets_count = assets_count

    if sampled_assets_count < assets_count:
        sampled_asset_ids_set = set(random.sample(mir_metadatas.attributes.keys(), sampled_assets_count))
        filter_mirdatas_by_asset_ids(mir_metadatas=mir_metadatas,
                                     mir_annotations=mir_annotations,
                                     asset_ids_set=sampled_asset_ids_set)


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    sampling_arg_parser = subparsers.add_parser('sampling',
                                                parents=[parent_parser],
                                                description='use this command to sample assets',
                                                help='sample assets')
    sampling_arg_parser.add_argument('--src-revs', dest='src_revs', type=str, help='rev@bid')
    sampling_arg_parser.add_argument('--dst-rev', dest='dst_rev', type=str, help='rev@tid')
    sampling_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    group = sampling_arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--count', dest='count', type=int, default=0, help='assets count')
    group.add_argument('--rate', dest='rate', type=float, default=0.0, help='assets sampling rate')
    sampling_arg_parser.set_defaults(func=CmdSampling)
