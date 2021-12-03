import argparse
import logging
from typing import List
from mir.scm.cmd import CmdScm
import os

from mir import scm
from mir.commands import base
from mir.tools import checker, class_ids
from mir.tools.code import MirCode


class CmdInit(base.BaseCommand):
    # private: misc
    @staticmethod
    def __update_files(mir_root: str) -> None:
        # creates a new label file if not exists
        label_file_path = class_ids.ids_file_path(mir_root=mir_root)
        if not os.path.isfile(label_file_path):
            with open(label_file_path, 'w') as f:
                f.write('# type_id, preserved, main type name, alias...\n')

    @staticmethod
    def __update_ignore(mir_root: str, git: CmdScm, ignored_items: List[str]) -> None:
        gitignore_file = os.path.join(mir_root, '.gitignore')
        with open(gitignore_file, 'a') as f:
            for item in ignored_items:
                f.write(f"{item}\n")
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

        CmdInit.__update_files(mir_root=mir_root)
        CmdInit.__update_ignore(mir_root=mir_root, git=repo_git, ignored_items=['.mir_lock', class_ids.ids_file_name()])
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
