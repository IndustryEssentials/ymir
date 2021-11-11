import os
import shutil
import subprocess
from typing import Type, List

from mir.commands.init import CmdInit
from mir.commands.checkout import CmdCheckout
from mir.commands.commit import CmdCommit
from mir.tools.code import MirCode


def dir_test_root(sub_dirs: List[str]) -> str:
    return os.path.join("/tmp/mir_cmd_test", '/'.join(sub_dirs))


# check enviroment
def check_commands():
    """
    test if mir, dvc, git command available
    """
    subprocess.run("dvc --version".split(" "), stdout=subprocess.DEVNULL)
    subprocess.run("git --version".split(" "), stdout=subprocess.DEVNULL)


# mir repo operations
def mir_repo_init(mir_root: str):
    return_code = CmdInit.run_with_args(mir_root)
    assert return_code == MirCode.RC_OK, "init failed"


def mir_repo_create_branch(mir_root: str, branch_name: str):
    assert len(branch_name) > 0
    return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=branch_name, branch_new=True)
    assert return_code == MirCode.RC_OK, "create branch failed"


def mir_repo_checkout(mir_root: str, branch_name: str):
    assert len(branch_name) > 0
    return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=branch_name, branch_new=False)
    assert return_code == MirCode.RC_OK, "checkout commit failed"


def mir_repo_commit_all(mir_root: str, mir_metadatas, mir_annotations, mir_keywords, mir_tasks, no_space_message: str):
    metadatas_path = os.path.join(mir_root, "metadatas.mir")
    annotations_path = os.path.join(mir_root, "annotations.mir")
    keywords_path = os.path.join(mir_root, "keywords.mir")
    tasks_path = os.path.join(mir_root, "tasks.mir")
    with open(metadatas_path, "wb") as m_f, \
         open(annotations_path, "wb") as a_f, \
         open(keywords_path, "wb") as k_f, \
         open(tasks_path, "wb") as t_f:
        m_f.write(mir_metadatas.SerializeToString())
        a_f.write(mir_annotations.SerializeToString())
        k_f.write(mir_keywords.SerializeToString())
        t_f.write(mir_tasks.SerializeToString())
    return_code = CmdCommit.run_with_args(mir_root=mir_root, msg=no_space_message)
    assert return_code == MirCode.RC_OK, "commit all failed"


def read_mir_pb(mir_root: str, mir_pb_type: Type):
    mir_pb_instance = mir_pb_type()
    with open(mir_root, "rb") as f:
        mir_pb_instance.ParseFromString(f.read())
    return mir_pb_instance


def remake_dirs(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
