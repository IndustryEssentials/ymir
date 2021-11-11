import argparse
import logging

from mir import scm
from mir.commands import base
from mir.tools import checker
from mir.tools.code import MirCode


class CmdBranch(base.BaseCommand):
    @staticmethod
    def run_with_args(mir_root: str, force_delete: str) -> int:
        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        # can not delete master branch
        if force_delete == "master":
            logging.info("can not delete master branch")
            return MirCode.RC_CMD_INVALID_BRANCH_OR_TAG

        cmd_opts = []
        if force_delete:
            cmd_opts.extend(["-D", force_delete])

        repo_git = scm.Scm(mir_root, scm_executable="git")
        output_str = repo_git.branch(cmd_opts)
        if output_str:
            logging.info("\n%s" % output_str)

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command branch: %s" % self.args)

        return CmdBranch.run_with_args(mir_root=self.args.mir_root, force_delete=self.args.force_delete)


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    branch_arg_parser = subparsers.add_parser("branch",
                                              parents=[parent_parser],
                                              description="use this command to show mir repo branches",
                                              help="show mir repo branches")
    delete_group = branch_arg_parser.add_mutually_exclusive_group()
    group = delete_group.add_mutually_exclusive_group()
    group.add_argument("-D", dest="force_delete", type=str, help="delete branch, even if branch not merged")
    branch_arg_parser.set_defaults(func=CmdBranch)
