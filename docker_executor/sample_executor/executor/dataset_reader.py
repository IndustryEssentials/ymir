from enum import IntEnum, auto
from typing import Iterator, Tuple

from executor import env


class DatasetType(IntEnum):
    UNKNOWN = auto()
    TRAINING = auto()
    VALIDATION = auto()
    CANDIDATE = auto()


def _index_file_for_dataset_type(env_config: env.EnvConfig, dataset_type: DatasetType) -> str:
    mapping = {
        DatasetType.TRAINING: env_config.input.training_index_file,
        DatasetType.VALIDATION: env_config.input.val_index_file,
        DatasetType.CANDIDATE: env_config.input.candidate_index_file,
    }
    return mapping[dataset_type]


def item_paths(dataset_type: DatasetType) -> Iterator[Tuple[str, str]]:
    file_path = _index_file_for_dataset_type(env.get_current_env(), dataset_type)
    if not file_path:
        raise ValueError(f"index file not set for dataset: {dataset_type}")

    with open(file_path, 'r') as f:
        for line in f:
            # note: last char of line is \n
            components = line.strip().split('\t')
            if len(components) == 2:
                yield (components[0], components[1])
            elif len(components) == 1:
                yield (components[0], '')
            else:
                raise ValueError(f"irregular index file: {file_path}")
