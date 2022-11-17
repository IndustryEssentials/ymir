import argparse
import logging

from mir.commands import base
from mir.tools.code import MirCode


class CmdFusion(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command fusion: %s", self.args)
        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    fusion_arg_parser = subparsers.add_parser("fusion",
                                              parents=[parent_parser],
                                              description="use this command to merge, filter and sampling assets",
                                              help="merge, filter and sampling assets")
    fusion_arg_parser.add_argument("--src-revs",
                                   dest="src_revs",
                                   type=str,
                                   required=True,
                                   help="source tvt types, revs and base task ids, first the host, others the guests, "
                                   "can begin with tr:/va:/te:, uses own tvt type if no prefix assigned")
    fusion_arg_parser.add_argument("--ex-src-revs",
                                   dest="ex_src_revs",
                                   type=str,
                                   help="branch(es) id, from which you want to exclude, seperated by comma.")
    fusion_arg_parser.add_argument('--cis', dest="in_cis", type=str, help="type names")
    fusion_arg_parser.add_argument('--ex-cis', dest="ex_cis", type=str, help="exclusive type names")
    sampling_group = fusion_arg_parser.add_mutually_exclusive_group(required=True)
    sampling_group.add_argument('--count', dest='count', type=int, default=0, help='assets count')
    sampling_group.add_argument('--rate', dest='rate', type=float, default=0.0, help='assets sampling rate')
    fusion_arg_parser.add_argument("--dst-rev", dest="dst_rev", type=str, help="rev@tid")
    fusion_arg_parser.add_argument('-w', dest='work_dir', type=str, required=False, help='working directory')
    fusion_arg_parser.set_defaults(func=CmdFusion)