import argparse
import logging

from mir import scm
from mir.commands import base
from mir.tools import checker
from mir.tools.code import MirCode


class CmdReset(base.BaseCommand):
    @staticmethod
    def run_with_args(mir_root: str, reset_hard: bool) -> int:
        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.IS_DIRTY])
        if return_code != MirCode.RC_OK:
            return return_code

        repo_git = scm.Scm(mir_root, scm_executable="git")
        output_str = repo_git.reset("--hard" if reset_hard else None)
        if output_str:
            logging.info("\n%s" % output_str)

        if reset_hard:
            repo_dvc = scm.Scm(mir_root, scm_executable="dvc")
            output_str = repo_dvc.checkout()
            if output_str:
                logging.info("\n%s" % output_str)

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command reset: %s", self.args)

        return CmdReset.run_with_args(self.args.mir_root, self.args.reset_hard)


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    reset_arg_parser = subparsers.add_parser("reset",
                                             parents=[parent_parser],
                                             description="use this command to undo changes to mir repo",
                                             help="undo changes to repo")
    reset_arg_parser.add_argument("--hard",
                                  dest="reset_hard",
                                  action="store_true",
                                  help="hard reset mode: undo add process and also undo the changes")
    reset_arg_parser.set_defaults(func=CmdReset)
