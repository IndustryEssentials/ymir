import argparse
import logging

from mir import scm
from mir.commands import base
from mir.tools import checker
from mir.tools.code import MirCode


class CmdLog(base.BaseCommand):
    @staticmethod
    def run_with_args(mir_root: str,
                      decorate: bool,
                      oneline: bool,
                      graph: bool,
                      dog: bool,
                      with_stdout: bool = False) -> int:
        return_code = checker.check(mir_root, [checker.Prerequisites.IS_INSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        cmd_opts = []
        if dog:
            decorate = True
            oneline = True
            graph = True
        if decorate:
            cmd_opts.append("--decorate")
        if oneline:
            cmd_opts.append("--oneline")
        if graph:
            cmd_opts.append("--graph")

        repo_git = scm.Scm(mir_root, scm_executable="git")
        output_str = repo_git.log(cmd_opts, with_stdout=with_stdout)
        if output_str:
            logging.info("\n%s" % output_str)

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command log: %s", self.args)

        return CmdLog.run_with_args(mir_root=self.args.mir_root,
                                    decorate=self.args.decorate,
                                    oneline=self.args.oneline,
                                    graph=self.args.graph,
                                    dog=self.args.dog)


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    log_arg_parser = subparsers.add_parser("log",
                                           parents=[parent_parser],
                                           description="use this command to show mir repo log",
                                           help="show mir repo log")
    log_arg_parser.add_argument("--oneline", help="print log in one line", action="store_true")
    log_arg_parser.add_argument("--decorate", help="print log in a pretty way", action="store_true")
    log_arg_parser.add_argument("--graph", help="print log in a graphic way", action="store_true")
    log_arg_parser.add_argument("--dog", help="print log in one line graphic pretty way", action="store_true")
    log_arg_parser.set_defaults(func=CmdLog)
