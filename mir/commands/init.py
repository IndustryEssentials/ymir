import argparse
import logging
from mir.scm.cmd import CmdScm
import os

from mir import scm
from mir.commands import base
from mir.tools import checker
from mir.tools.code import MirCode


class CmdInit(base.BaseCommand):
    # private: modify_ignore
    @staticmethod
    def __ignore_lock(mir_root: str, git: CmdScm) -> None:
        gitignore_file = os.path.join(mir_root, '.gitignore')
        with open(gitignore_file, 'a') as f:
            f.write('.mir_lock\n')
        git.add(gitignore_file)

    # public: run
    @staticmethod
    def run_with_args(mir_root: str) -> int:
        return_code = checker.check(
            mir_root, [checker.Prerequisites.IS_OUTSIDE_GIT_REPO, checker.Prerequisites.IS_OUTSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        repo_git = scm.Scm(root_dir=mir_root, scm_executable='git')
        repo_dvc = scm.Scm(root_dir=mir_root, scm_executable='dvc')
        repo_git.init()
        repo_dvc.init()

        CmdInit.__ignore_lock(mir_root, repo_git)
        repo_git.commit(["-m", "first commit"])

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command init: %s", self.args)

        return self.run_with_args(mir_root=self.args.mir_root)


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:  # pragma: no cover
    init_arg_parser = subparsers.add_parser("init",
                                            parents=[parent_parser],
                                            description="use this command to init mir repo",
                                            help="init mir repo")
    init_arg_parser.set_defaults(func=CmdInit)
