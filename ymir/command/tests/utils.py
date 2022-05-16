import os
import shutil
import subprocess
from typing import List, Type

import yaml

from mir.commands.init import CmdInit
from mir.commands.checkout import CmdCheckout
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids
from mir.tools.code import MirCode
from mir.tools.mir_storage_ops import MirStorageOps


def dir_test_root(sub_dirs: List[str]) -> str:
    return os.path.join("/tmp/mir_cmd_test", '/'.join(sub_dirs))


# check enviroment
def check_commands():
    """
    test if git command available
    """
    subprocess.run("git --version".split(" "), stdout=subprocess.DEVNULL)


# mir repo operations
def mir_repo_init(mir_root: str):
    return_code = CmdInit.run_with_args(mir_root, empty_rev='')
    assert return_code == MirCode.RC_OK, "init failed"


def mir_repo_create_branch(mir_root: str, branch_name: str):
    assert len(branch_name) > 0
    return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=branch_name, branch_new=True)
    assert return_code == MirCode.RC_OK, "create branch failed"


def mir_repo_checkout(mir_root: str, branch_name: str):
    assert len(branch_name) > 0
    return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=branch_name, branch_new=False)
    assert return_code == MirCode.RC_OK, "checkout commit failed"


def read_mir_pb(mir_root: str, mir_pb_type: Type):
    mir_pb_instance = mir_pb_type()
    with open(mir_root, "rb") as f:
        mir_pb_instance.ParseFromString(f.read())
    return mir_pb_instance


def remake_dirs(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def prepare_labels(mir_root: str, names: List[str]):
    labels: List[class_ids._SingleLabel] = []
    for idx, name in enumerate(names):
        components = name.split(',')
        labels.append(class_ids._SingleLabel(id=idx, name=components[0], aliases=components[1:]))
    label_storage = class_ids._LabelStorage(labels=labels)

    with open(class_ids.ids_file_path(mir_root=mir_root), 'w') as f:
        yaml.safe_dump(label_storage.dict(), f)
