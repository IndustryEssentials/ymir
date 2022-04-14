"""
# contents of env.yaml
```
task_id: task0
training_index: /in/train-index.tsv
config: /in/config.yaml
```

# dir structure
"""

from enum import IntEnum, auto
from typing import Iterator, Tuple


class DatasetType(IntEnum):
    UNKNOWN = auto()
    TRAINING = auto()
    VALIDATION = auto()


_env_file_path_: str = 'env.yaml'


def set_env(env_file_path: str) -> None:
    _env_file_path_ = env_file_path


class input:
    @staticmethod
    def get_dataset_item_paths(dataset_type: DatasetType) -> Iterator[Tuple[str, str]]:
        pass

    @staticmethod
    def get_model_dir() -> str:
        pass

    @staticmethod
    def get_config_path() -> str:
        pass


class output:
    @staticmethod
    def get_model_dir() -> str:
        pass

    def get_tensorboard_dir() -> None:
        pass
