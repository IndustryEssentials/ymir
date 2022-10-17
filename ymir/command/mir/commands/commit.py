import argparse
import logging
import os

from mir import scm
from mir.commands import base
from mir.tools import checker, mir_repo_utils
from mir.tools.code import MirCode


class CmdCommit(base.BaseCommand):
    @staticmethod
    def run_with_args(mir_root: str, msg: str) -> int:
        return_code = checker.check(mir_root,
                                    [checker.Prerequisites.IS_INSIDE_MIR_REPO, checker.Prerequisites.IS_DIRTY])
        if return_code != MirCode.RC_OK:
            return return_code

        extra_items = mir_repo_utils.find_extra_items(mir_root=mir_root)
        if extra_items:
            logging.error(f"extra items: {', '.join(extra_items)}")
            return MirCode.RC_CMD_INVALID_MIR_REPO

        repo_git = scm.Scm(root_dir=mir_root, scm_executable='git')
        git_attr_path = os.path.join(mir_root, '.gitattributes')
        if _need_to_update_git_attr(git_attr_path):
            with open(git_attr_path, 'w') as f:
                f.write('*.mir binary\n')
        repo_git.add('.')
        repo_git.commit(["-m", msg])

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command commit: %s", self.args)

        return CmdCommit.run_with_args(mir_root=self.args.mir_root, msg=self.args.cmt_msg)


def _need_to_update_git_attr(git_attr_path: str) -> bool:
    if not os.path.isfile(git_attr_path):
        return True
    with open(git_attr_path, 'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        if line == '*.mir binary':
            return False
    return True


def bind_to_subparsers(subparsers: argparse._SubParsersAction,
                       parent_parser: argparse.ArgumentParser) -> None:
    commit_arg_parser = subparsers.add_parser("commit",
                                              parents=[parent_parser],
                                              description="use this command to commit changes",
                                              help="commit changes")
    commit_arg_parser.add_argument("-m", dest="cmt_msg", type=str, help="message of this commit")
    commit_arg_parser.set_defaults(func=CmdCommit)
