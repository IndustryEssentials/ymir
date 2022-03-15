import argparse
import logging

from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import checker, revs_parser
from mir.tools.code import MirCode
from mir.tools.command_run_in_out import command_run_in_out
from mir.tools.errors import MirRuntimeError


class CmdModelImport(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command import-model: %s", self.args)

        return CmdModelImport.run_with_args(mir_root=self.args.mir_root,
                                            dst_rev=self.args.dst_rev,
                                            src_revs='master',
                                            work_dir=self.args.work_dir,
                                            package_path=self.args.package_path)

    @staticmethod
    @command_run_in_out
    def run_with_args(mir_root: str, dst_rev: str, src_revs: str, work_dir: str, package_path: str) -> int:
        if not src_revs:
            logging.error('empty --src-revs')
            return MirCode.RC_CMD_INVALID_ARGS
        src_typ_rev_tid = revs_parser.parse_single_arg_rev(src_revs)
        if checker.check_src_revs(src_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS
        if not dst_rev:
            logging.error("empty --dst-rev")
            return MirCode.RC_CMD_INVALID_ARGS
        dst_typ_rev_tid = revs_parser.parse_single_arg_rev(dst_rev)
        if checker.check_dst_rev(dst_typ_rev_tid) != MirCode.RC_OK:
            return MirCode.RC_CMD_INVALID_ARGS

        if not package_path:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty package_path')

        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    importing_arg_parser = subparsers.add_parser("import-model",
                                                 parents=[parent_parser],
                                                 description="use this command to import model package",
                                                 help="import model")
    importing_arg_parser.add_argument("--package-path",
                                      dest="package_path",
                                      type=str,
                                      required=True,
                                      help="path to model package file")
    importing_arg_parser.add_argument("--dst-rev",
                                      dest="dst_rev",
                                      type=str,
                                      required=True,
                                      help="rev@tid: destination branch name and task id")
    importing_arg_parser.add_argument('-w', dest='work_dir', type=str, required=True, help='working directory')
    importing_arg_parser.set_defaults(func=CmdModelImport)
