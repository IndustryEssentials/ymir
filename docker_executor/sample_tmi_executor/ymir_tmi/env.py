"""

## contents of env.yaml
```
task_id: task0
run_training: True
run_mining: True
run_infer: True
input:
    root_dir: /in
    assets_dir: assets
    annotations_dir: annotations
    models_dir: models
    training_index_file: train-index.tsv
    val_index_file: val-index.tsv
    candidate_index_file: candidate-index.tsv
    config_file: config.yaml
output:
    root_dir: /out
    models_dir: models
    tensorboard_dir: tensorboard
    training_result_file: result.yaml
    mining_result_file: result.txt
    infer_result_file: infer-result.yaml
    monitor_file: monitor.txt
```

## dir and file structure
```
/in/assets
/in/annotations
/in/train-index.tsv
/in/val-index.tsv
/in/candidate-index.tsv
/in/config.yaml
/in/env.yaml
/out/models
/out/tensorboard
/out/monitor.txt
/out/monitor-log.txt
/out/ymir-executor-out.log
```

"""

from enum import IntEnum, auto
import logging
import sys
from typing import Iterator, Tuple

from pydantic import BaseModel
import yaml


class DatasetType(IntEnum):
    UNKNOWN = auto()
    TRAINING = auto()
    VALIDATION = auto()
    CANDIDATE = auto()


class EnvInputConfig(BaseModel):
    root_dir: str = '/in'
    assets_dir: str = '/in/assets'
    annotations_dir: str = '/in/annotations'
    models_dir: str = '/in/models'
    training_index_file: str = ''
    val_index_file: str = ''
    candidate_index_file: str = ''
    config_file: str = '/in/config.yaml'

    def _index_file_for_dataset_type(self, dataset_type: DatasetType) -> str:
        mapping = {
            DatasetType.TRAINING: self.training_index_file,
            DatasetType.VALIDATION: self.val_index_file,
            DatasetType.CANDIDATE: self.candidate_index_file,
        }
        return mapping[dataset_type]

    def dataset_item_paths(self, dataset_type: DatasetType) -> Iterator[Tuple[str, str]]:
        file_path = self._index_file_for_dataset_type(dataset_type)
        with open(file_path, 'r') as f:
            for line in f:
                # note: last char of line is \n
                components = line[:-1].split('\t')
                if len(components) == 2:
                    yield (components[0], components[1])
                elif len(components) == 1:
                    yield (components[0], '')
                else:
                    logging.info(f"len {len(components)}")  # for test
                    raise ValueError(f"irregular index file: {file_path}")


class EnvOutputConfig(BaseModel):
    root_dir: str = '/out'
    models_dir: str = '/out/models'
    tensorboard_dir: str = '/out/tensorboard'
    training_result_file: str = '/out/models/result.yaml'
    mining_result_file: str = '/out/result.tsv'
    infer_result_file: str = '/out/infer-result.json'
    monitor_file: str = '/out/monitor.txt'


class EnvConfig(BaseModel):
    task_id: str = 'default-task'
    run_training: bool = False
    run_mining: bool = False
    run_infer: bool = False

    input: EnvInputConfig = EnvInputConfig()
    output: EnvOutputConfig = EnvOutputConfig()


_env_config_: EnvConfig = EnvConfig()


logging.basicConfig(stream=sys.stdout,
                    format='%(levelname)-8s: [%(asctime)s] %(message)s',
                    datefmt='%Y%m%d-%H:%M:%S',
                    level=logging.INFO)


def set_env(env_file_path: str) -> EnvConfig:
    with open(env_file_path, 'r') as f: 
        global _env_config_
        _env_config_ = EnvConfig.parse_obj(yaml.safe_load(f.read()))


def get_current_env() -> EnvConfig:
    return _env_config_


def get_executor_config() -> dict:
    with open(get_current_env().input.config_file, 'r') as f:
        executor_config = yaml.safe_load(f)
    return executor_config
