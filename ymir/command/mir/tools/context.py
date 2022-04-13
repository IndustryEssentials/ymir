import os
from typing import List

import yaml

from mir.tools import class_ids
from mir.tools import utils as mir_utils


def context_file_path_from_mir_root(mir_root: str) -> str:
    return os.path.join(mir_utils.repo_dot_mir_path(mir_root=mir_root), 'context.yaml')


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

    with open(context_file_path, 'w') as f:
        yaml.safe_dump({'project': {'class_ids': project_class_ids}}, f)


# general
def check_class_names(mir_root: str, current_class_names: List[str]) -> bool:
    """
    check `current_class_names` matches mir repo's project class ids settings

    if mir repo has project class ids settings, this function returns True if they are equal

    if mir repo has no project class ids settings, this function always returns True, meaning they are always matched
    """
    class_id_manager = class_ids.ClassIdManager(mir_root)
    current_class_ids = class_id_manager.id_for_names(current_class_names)
    return check_class_ids(mir_root=mir_root, current_class_ids=current_class_ids)


def check_class_ids(mir_root: str, current_class_ids: List[int]) -> bool:
    """
    check `current_class_ids` matches mir repo's project class ids settings

    if mir repo has project class ids settings, this function returns True if they are equal

    if mir repo has no project class ids settings, this function always returns True, meaning they are always matched
    """
    project_class_ids = load(mir_root=mir_root)
    if not project_class_ids:
        # if this mir repo not binded to project, treat as equal
        return True
    return project_class_ids == current_class_ids
