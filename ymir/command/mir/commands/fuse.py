import argparse
import logging

from mir.commands import base
from mir.tools import mir_storage_ops
from mir.tools.code import MirCode
from mir.tools.annotations import filter_mirdatas_by_asset_ids, map_and_filter_annotations


class CmdFuse(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command fuse: %s", self.args)
        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    fuse_arg_parser = subparsers.add_parser("fuse",
                                            parents=[parent_parser],
                                            description="use this command to merge, filter and sampling assets",
                                            help="merge, filter and sampling assets")
    fuse_arg_parser.add_argument("--src-revs",
                                 dest="src_revs",
                                 type=str,
                                 required=True,
                                 help="source tvt types, revs and base task ids, first the host, others the guests, "
                                 "can begin with tr:/va:/te:, uses own tvt type if no prefix assigned")
    fuse_arg_parser.add_argument("--ex-src-revs",
                                 dest="ex_src_revs",
                                 type=str,
                                 help="branch(es) id, from which you want to exclude, seperated by comma.")
    fuse_arg_parser.add_argument('--cis', dest="in_cis", type=str, help="type names")
    fuse_arg_parser.add_argument('--ex-cis', dest="ex_cis", type=str, help="exclusive type names")
    sampling_group = fuse_arg_parser.add_mutually_exclusive_group(required=True)
    sampling_group.add_argument('--count', dest='count', type=int, default=0, help='assets count')
    sampling_group.add_argument('--rate', dest='rate', type=float, default=0.0, help='assets sampling rate')
    fuse_arg_parser.add_argument("--dst-rev", dest="dst_rev", type=str, help="rev@tid")
    fuse_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    fuse_arg_parser.set_defaults(func=CmdFuse)
