from dataclasses import asdict, dataclass, field
import os
from typing import List

import yaml


@dataclass
class ProjectContextConfig:
    class_ids: List[int] = field(default_factory=list)


@dataclass
class ContextConfig:
    project: ProjectContextConfig = field(default_factory=ProjectContextConfig)


class ContextManager:
    def __init__(self, mir_root: str) -> None:
        self._context_file_path = self.context_file_path_from_mir_root(mir_root=mir_root)

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

    @classmethod
    def context_file_path_from_mir_root(cls, mir_root: str) -> str:
        return os.path.join(mir_root, '.mir', 'context.yaml')
