import argparse
import logging

from mir.commands import base
from mir.tools import checker, mir_repo_utils
from mir.tools.code import MirCode


class CmdStatus(base.BaseCommand):
    def run(self) -> int:
        logging.debug("command status: %s", self.args)

        return self.run_with_args(mir_root=self.args.mir_root)

    @staticmethod
    def run_with_args(mir_root: str) -> int:
        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        repo_dirty = mir_repo_utils.mir_check_repo_git_dirty(mir_root=mir_root)
        logging.info('repo: dirty' if repo_dirty else 'repo: clean')

        return MirCode.RC_OK


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:
    status_arg_parser = subparsers.add_parser("status",
                                              parents=[parent_parser],
                                              description="use this command to show current workspace status",
                                              help="show current workspace status")
    status_arg_parser.set_defaults(func=CmdStatus)
