import linecache
import os
from pydantic import BaseModel

import yaml

from mir import version
from mir.tools import settings as mir_settings


# see also: sample_executor/ef/env.py
class _EnvInputConfig(BaseModel):
    root_dir: str = '/in'
    assets_dir: str = '/in/assets'
    annotations_dir: str = '/in/annotations'
    models_dir: str = '/in/models'
    training_index_file: str = ''
    val_index_file: str = ''
    candidate_index_file: str = ''
    config_file: str = '/in/config.yaml'


class _EnvOutputConfig(BaseModel):
    root_dir: str = '/out'
    models_dir: str = '/out/models'
    tensorboard_dir: str = '/out/tensorboard'
    training_result_file: str = '/out/models/result.yaml'
    mining_result_file: str = '/out/result.tsv'
    infer_result_file: str = '/out/infer-result.json'
    monitor_file: str = '/out/monitor.txt'
    executor_log_file: str = '/out/ymir-executor-out.log'


class _EnvConfig(BaseModel):
    protocol_version = version.TMI_PROTOCOL_VERSION
    task_id: str = 'default-task'
    run_training: bool = False
    run_mining: bool = False
    run_infer: bool = False

    input: _EnvInputConfig = _EnvInputConfig()
    output: _EnvOutputConfig = _EnvOutputConfig()

    manifest_file: str = '/img-man/manifest.yaml'


def generate_training_env_config_file(task_id: str, env_config_file_path: str) -> None:
    env_config = _EnvConfig()
    env_config.task_id = task_id
    env_config.run_training = True
    env_config.input.training_index_file = '/in/train-index.tsv'
    env_config.input.val_index_file = '/in/val-index.tsv'

    with open(env_config_file_path, 'w') as f:
        yaml.safe_dump(env_config.dict(), f)


def generate_mining_infer_env_config_file(task_id: str, run_mining: bool, run_infer: bool,
                                          env_config_file_path: str) -> None:
    # TODO: seperate command mining and infer
    env_config = _EnvConfig()
    env_config.task_id = task_id
    env_config.run_mining = run_mining
    env_config.run_infer = run_infer
    env_config.input.candidate_index_file = '/in/candidate-index.tsv'

    with open(env_config_file_path, 'w') as f:
        yaml.safe_dump(env_config.dict(), f)


def collect_executor_outlog_tail(work_dir: str, tail_line_count: int = 5) -> str:
    out_log_path = os.path.join(work_dir, 'out', mir_settings.EXECUTOR_OUTLOG_NAME)
    if not os.path.isfile(out_log_path):
        return ''

    tail_lines = linecache.getlines(out_log_path)[-1 * tail_line_count:]
    if not tail_lines:
        return ''

    joint_tail_lines = ''.join(tail_lines)
    return f"EXECUTOR OUTLOG TAIL FROM: {out_log_path}\n{joint_tail_lines}"
