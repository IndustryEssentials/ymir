import argparse
import logging

from mir import scm
from mir.commands import base
from mir.tools import checker
from mir.tools.code import MirCode


class CmdCheckout(base.BaseCommand):
    @staticmethod
    def run_with_args(mir_root: str, commit_id: str, branch_new: bool = False) -> int:
        return_code = checker.check(mir_root)
        if return_code != MirCode.RC_OK:
            return return_code

        repo_git = scm.Scm(root_dir=mir_root, scm_executable='git')

        # git options
        cmd_opts = []
        if branch_new:
            cmd_opts.append("-b")
        cmd_opts.append(commit_id)

        output_str = repo_git.checkout(cmd_opts)
        if output_str:
            logging.info("\n%s" % output_str)

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command checkout: %s", self.args)

        return CmdCheckout.run_with_args(mir_root=self.args.mir_root,
                                         branch_new=self.args.branch_new,
                                         commit_id=self.args.commit_id)


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:
    checkout_arg_parser = subparsers.add_parser("checkout",
                                                aliases=["co"],
                                                parents=[parent_parser],
                                                description="use this command to show mir repo branches",
                                                help="checkout commits or add new branches")
    checkout_arg_parser.add_argument("-b", dest="branch_new", help="add a new branch", action="store_true")
    checkout_arg_parser.add_argument("commit_id", help="destination commit id or tag name", nargs=1, type=str)
    checkout_arg_parser.set_defaults(func=CmdCheckout)
