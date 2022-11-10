import os
import shutil
import subprocess
from typing import Any, List, Type

import yaml

from mir.commands.init import CmdInit
from mir.commands.checkout import CmdCheckout
from mir.tools import class_ids
from mir.tools.code import MirCode


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
    return_code = CmdInit.run_with_args(mir_root=mir_root,
                                        label_storage_file=class_ids.ids_file_path(mir_root),
                                        empty_rev='')
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
    labels: List[class_ids.SingleLabel] = []
    for idx, name in enumerate(names):
        components = name.split(',')
        labels.append(class_ids.SingleLabel(id=idx, name=components[0], aliases=components[1:]))
    label_storage = class_ids.LabelStorage(labels=labels)

    with open(class_ids.ids_file_path(mir_root=mir_root), 'w') as f:
        yaml.safe_dump(label_storage.dict(), f)


def diff_dicts(a_dict: dict, b_dict: dict, stack: list) -> None:
    if set(a_dict.keys()) != set(b_dict.keys()):
        raise ValueError(f"stack: {stack} keys mismatched\na: {sorted(a_dict.keys())}\nb: {sorted(b_dict.keys())}")
    for ka in a_dict:
        va = a_dict[ka]
        vb = b_dict[ka]
        diff_types(va, vb, stack=stack + [ka])
        if isinstance(va, dict):
            diff_dicts(a_dict=va, b_dict=vb, stack=stack + [ka])
        else:
            diff_others(a=va, b=vb, stack=stack + [ka])


def diff_types(a: Any, b: Any, stack: list) -> None:
    if not isinstance(a, type(b)) and not isinstance(b, type(a)):
        raise ValueError(f"stack: {stack} types mismatched: {type(a)} vs {type(b)}")


def diff_others(a: Any, b: Any, stack: list) -> None:
    if a != b:
        raise ValueError(f"stack: {stack}, other kind of values mismatched:\na: {a}\nb: {b}")
