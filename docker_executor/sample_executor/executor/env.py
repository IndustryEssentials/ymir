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

from pydantic import BaseModel
import yaml

from executor import settings


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


def get_current_env() -> EnvConfig:
    with open(settings.DEFAULT_ENV_FILE_PATH, 'r') as f:
        return EnvConfig.parse_obj(yaml.safe_load(f.read()))


def get_executor_config() -> dict:
    with open(get_current_env().input.config_file, 'r') as f:
        executor_config = yaml.safe_load(f)
    return executor_config
