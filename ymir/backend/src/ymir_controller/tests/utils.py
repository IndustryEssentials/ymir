import os
import subprocess
from typing import Any, List
from unittest import mock

from common_utils.labels import ids_file_name


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


def user_label_file(sandbox_root: str, user_id: str) -> str:
    return os.path.join(sandbox_root, user_id, ids_file_name())


def mocked_index_call(user_id: str, repo_id: str, task_id: str) -> Any:
    index_command = [
        './hel_server', 'viewer_client', '--user_id', user_id, '--repo_id', repo_id, '--task_id', task_id, 'index'
    ]
    return mock.call(index_command, capture_output=True, text=True, cwd='/app/ymir_hel')
