import os
import shutil
import subprocess
from typing import Type, List

from mir.commands.init import CmdInit
from mir.commands.checkout import CmdCheckout
from mir.protos import mir_command_pb2 as mirpb
from mir.tools.code import MirCode
from mir.tools.mir_storage_ops import MirStorageOps


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


def mir_repo_commit_all(mir_root: str, mir_metadatas, mir_annotations, mir_tasks, no_space_message: str, task_id: str,
                        src_branch: str, dst_branch: str):
    mir_datas = {
        mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
        mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
        mirpb.MirStorage.MIR_TASKS: mir_tasks,
    }
    return_code = MirStorageOps.save_and_commit(mir_root=mir_root,
                                                mir_branch=dst_branch,
                                                task_id=task_id,
                                                his_branch=src_branch,
                                                mir_datas=mir_datas,
                                                commit_message=no_space_message)
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
