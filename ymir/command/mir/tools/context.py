import os
from typing import List
from mir.tools.errors import MirRuntimeError

import yaml

from mir.tools import class_ids
from mir.tools.code import MirCode


def context_file_path_from_mir_root(mir_root: str) -> str:
    return os.path.join(mir_root, '.mir', 'context.yaml')


# save and load
def load(mir_root: str) -> List[int]:
    context_file_path = context_file_path_from_mir_root(mir_root)
    if not os.path.isfile(context_file_path):
        return []

    with open(context_file_path, 'r') as f:
        context_obj = yaml.safe_load(f)
        return context_obj.get('project', {}).get('class_ids', [])


def save(mir_root: str, project_class_ids: List[int]) -> None:
    context_file_path = context_file_path_from_mir_root(mir_root)
    os.makedirs(os.path.dirname(context_file_path), exist_ok=True)

    with open(context_file_path, 'w') as f:
        yaml.safe_dump({'project': {'class_ids': project_class_ids}}, f)


# general
def check_class_names(mir_root: str, current_class_names: List[str]) -> None:
    class_id_manager = class_ids.ClassIdManager(mir_root)
    current_class_ids = class_id_manager.id_for_names(current_class_names)
    check_class_ids(mir_root=mir_root, current_class_ids=current_class_ids)


def check_class_ids(mir_root: str, current_class_ids: List[int]) -> None:
    project_class_ids = load(mir_root=mir_root)
    if not project_class_ids:
        return

    if project_class_ids != current_class_ids:
        raise MirRuntimeError(
            error_code=MirCode.RC_CMD_INVALID_ARGS,
            error_message=f"class ids mismatch: current {current_class_ids} vs project {project_class_ids}")
