from dataclasses import asdict, dataclass, field
import os
from typing import List
from mir.tools.errors import MirRuntimeError

import yaml

from mir.tools import class_ids
from mir.tools.code import MirCode


@dataclass
class ProjectContextConfig:
    class_ids: List[int] = field(default_factory=list)


@dataclass
class ContextConfig:
    project: ProjectContextConfig = field(default_factory=ProjectContextConfig)


class ContextManager:
    def __init__(self, mir_root: str) -> None:
        self._mir_root = mir_root
        self._context_file_path = self.context_file_path_from_mir_root(mir_root=mir_root)

    # save and load
    def load(self) -> ContextConfig:
        if not os.path.isfile(self._context_file_path):
            return ContextConfig()

        with open(self._context_file_path, 'r') as f:
            context_obj = yaml.safe_load(f)
            return ContextConfig(project=ProjectContextConfig(**context_obj['project']))

    def save(self, context_config: ContextConfig) -> None:
        os.makedirs(os.path.dirname(self._context_file_path), exist_ok=True)

        with open(self._context_file_path, 'w') as f:
            yaml.safe_dump(asdict(context_config), f)

    # public: general
    def check_class_names(self, current_class_names: List[str]) -> None:
        class_id_manager = class_ids.ClassIdManager(mir_root=self._mir_root)
        current_class_ids = class_id_manager.id_for_names(current_class_names)
        self.check_class_ids(current_class_ids=current_class_ids)

    def check_class_ids(self, current_class_ids: List[int]) -> None:
        project_class_ids = self.load().project.class_ids
        if not project_class_ids:
            return
        if project_class_ids != current_class_ids:
            raise MirRuntimeError(
                error_code=MirCode.RC_CMD_INVALID_ARGS,
                error_message=f"class ids mismatch: current {current_class_ids} vs project {project_class_ids}")

    @classmethod
    def context_file_path_from_mir_root(cls, mir_root: str) -> str:
        return os.path.join(mir_root, '.mir', 'context.yaml')
