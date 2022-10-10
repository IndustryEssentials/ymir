
import os
import re
from typing import List

import yaml

from mir.scm.cmd import CmdScm


# repo funcs
def get_repo_tags(mir_root: str) -> List[str]:
    git_cmd = CmdScm(working_dir=mir_root, scm_executable='git')
    tags: str = git_cmd.tag()
    return sorted(tags.splitlines())


def remove_old_tag(mir_root: str, tag: str) -> None:
    git_cmd = CmdScm(working_dir=mir_root, scm_executable='git')
    git_cmd.tag(['-d', tag])


# detect models
def get_model_hashes(models_root: str) -> List[str]:
    return [
        h for h in os.listdir(models_root)
        if re.match(pattern=r'^.{40}$', string=h) and os.path.isfile(os.path.join(models_root, h))
    ]


def get_model_class_names(serialized_executor_config: str) -> List[str]:
    if not serialized_executor_config:
        return []

    executor_config = yaml.safe_load(serialized_executor_config)
    return executor_config.get('class_names', [])
