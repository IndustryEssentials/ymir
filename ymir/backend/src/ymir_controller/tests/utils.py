import os
import subprocess
from typing import List


def dir_test_root(sub_dirs: List[str]) -> str:
    return os.path.join('/tmp/ymir-controller-sandbox-root/unit-test', '/'.join(sub_dirs))


# check enviroment
def check_commands():
    """
    test if mir, git command available
    """
    subprocess.run("mir --version".split(" "), stdout=subprocess.DEVNULL)
    subprocess.run("git --version".split(" "), stdout=subprocess.DEVNULL)


# mir repo operations
def mir_repo_init(mir_root: str):
    mir_init_cmd = "mir init -r {}".format(mir_root)
    subprocess.run(mir_init_cmd.split(" "), stdout=subprocess.DEVNULL)
    command = "git add ."
    subprocess.run(command.split(" "), cwd=mir_root, stdout=subprocess.DEVNULL)
    command = "git commit -m init"
    subprocess.run(command.split(" "), cwd=mir_root, stdout=subprocess.DEVNULL)


def mir_repo_create_branch(mir_root: str, branch_name: str):
    assert (len(branch_name) > 0)
    mir_checkout_cmd = "mir checkout -b -r {} {}".format(mir_root, branch_name)
    subprocess.run(mir_checkout_cmd.split(" "), stdout=subprocess.DEVNULL)
