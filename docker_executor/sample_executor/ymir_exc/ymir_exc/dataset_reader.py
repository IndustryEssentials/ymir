from typing import Iterator, Tuple

from ymir_exc import env


def _index_file_for_dataset_type(env_config: env.EnvConfig, dataset_type: env.DatasetType) -> str:
    mapping = {
        env.DatasetType.TRAINING: env_config.input.training_index_file,
        env.DatasetType.VALIDATION: env_config.input.val_index_file,
        env.DatasetType.CANDIDATE: env_config.input.candidate_index_file,
    }
    return mapping[dataset_type]


def item_paths(dataset_type: env.DatasetType) -> Iterator[Tuple[str, str]]:
    file_path = _index_file_for_dataset_type(env.get_current_env(), dataset_type)
    if not file_path:
        raise ValueError(f"index file not set for dataset: {dataset_type}")

    with open(file_path, 'r') as f:
        for line in f:
            # note: last char of line is \n
            components = line.strip().split('\t')
            if len(components) >= 2:
                yield (components[0], components[1])
            elif len(components) == 1:
                yield (components[0], '')
            else:
                # ignore empty lines
                continue


def items_count(dataset_type: env.DatasetType) -> int:
    return len(list(item_paths(dataset_type=dataset_type)))
