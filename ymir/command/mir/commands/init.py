import argparse
import logging
from typing import List
import os

from mir import scm
from mir.commands import base
from mir.protos import mir_command_pb2 as mirpb
from mir.scm.cmd import CmdScm
from mir.tools import checker, class_ids, mir_storage_ops, revs_parser
from mir.tools.code import MirCode


class CmdInit(base.BaseCommand):
    # private: misc
    @staticmethod
    def __update_ignore(mir_root: str, git: CmdScm, ignored_items: List[str]) -> None:
        gitignore_file = os.path.join(mir_root, '.gitignore')
        with open(gitignore_file, 'a') as f:
            for item in ignored_items:
                f.write(f"{item}\n")
        git.add(gitignore_file)

    @staticmethod
    def __commit_empty_dataset(mir_root: str, empty_rev: str) -> None:
        if not empty_rev:
            return

        dst_rev_tid = revs_parser.parse_single_arg_rev(empty_rev, need_tid=True)

        mir_metadatas = mirpb.MirMetadatas()
        mir_annotations = mirpb.MirAnnotations()
        task = mir_storage_ops.create_task(task_type=mirpb.TaskTypeInit,
                                           task_id=dst_rev_tid.tid,
                                           message='init empty dataset',
                                           src_revs='master',
                                           dst_rev=empty_rev)
        mir_datas = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                      mir_branch=dst_rev_tid.rev,
                                                      his_branch='master',
                                                      mir_datas=mir_datas,
                                                      task=task)

    # public: run
    @staticmethod
    def run_with_args(mir_root: str, empty_rev: str) -> int:
        return_code = checker.check(
            mir_root, [checker.Prerequisites.IS_OUTSIDE_GIT_REPO, checker.Prerequisites.IS_OUTSIDE_MIR_REPO])
        if return_code != MirCode.RC_OK:
            return return_code

        class_ids.create_empty_if_not_exists(mir_root=mir_root)

        repo_git = scm.Scm(root_dir=mir_root, scm_executable='git')
        repo_git.init()
        repo_git.config(['core.fileMode', 'false'])

        CmdInit.__update_ignore(mir_root=mir_root, git=repo_git, ignored_items=['.mir_lock', '.mir'])
        repo_git.commit(["-m", "first commit"])

        # creates an empty dataset if empty_rev provided
        CmdInit.__commit_empty_dataset(mir_root=mir_root, empty_rev=empty_rev)

        return MirCode.RC_OK

    def run(self) -> int:
        logging.debug("command init: %s", self.args)

        return self.run_with_args(mir_root=self.args.mir_root,
                                  empty_rev=self.args.empty_rev)


def bind_to_subparsers(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser) -> None:
    init_arg_parser = subparsers.add_parser("init",
                                            parents=[parent_parser],
                                            description="use this command to init mir repo",
                                            help="init mir repo")
    init_arg_parser.add_argument('--with-empty-rev',
                                 dest='empty_rev',
                                 required=False,
                                 type=str,
                                 default='',
                                 help='rev@tid, if provided, also creates an empty dataset in this branch')
    init_arg_parser.set_defaults(func=CmdInit)
