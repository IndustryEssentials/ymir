from functools import wraps
import linecache
import logging
import os
import pathlib
import time
import shutil
import tarfile
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from google.protobuf import json_format
from pydantic import BaseModel, root_validator
import yaml

from mir import scm
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import hash_utils, settings as mir_settings
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


def time_it(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: Dict) -> Callable:
        _start = time.time()
        _ret = f(*args, **kwargs)
        _cost = time.time() - _start
        logging.info(f"|-{f.__name__} costs {_cost:.2f}s({_cost / 60:.2f}m).")
        return _ret

    return wrapper


# project
def project_root() -> str:
    root = str(pathlib.Path(__file__).parent.parent.parent.absolute())
    return root


# mir repo infos
def mir_repo_head_name(git: Union[str, scm.CmdScm]) -> Optional[str]:
    """ get current mir repo head name (may be branch, or commit id) """
    git_scm = None
    if isinstance(git, str):
        git_scm = scm.Scm(git, scm_executable="git")
    elif isinstance(git, scm.CmdScm):
        git_scm = git
    else:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="invalid git: needs str or CmdScm")

    git_result = git_scm.rev_parse(["--abbrev-ref", "HEAD"])
    if isinstance(git_result, str):
        return git_result
    elif isinstance(git_result, bytes):
        return git_result.decode("utf-8")
    return str(git_result)


def mir_repo_commit_id(git: Union[str, scm.CmdScm], branch: str = "HEAD") -> str:
    """ get mir repo branch's commit id """
    git_scm = None
    if isinstance(git, str):
        git_scm = scm.Scm(git, scm_executable="git")
    elif isinstance(git, scm.CmdScm):
        git_scm = git
    else:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="invalid git: needs str or CmdScm")

    git_result = git_scm.rev_parse(branch)
    if isinstance(git_result, str):
        return git_result
    elif isinstance(git_result, bytes):
        return git_result.decode("utf-8")
    return str(git_result)


# assets
def get_asset_storage_path(location: str, hash: str, make_dirs: bool) -> str:
    sub_dir = os.path.join(location, hash[-2:])
    if make_dirs:
        os.makedirs(sub_dir, exist_ok=True)
    return os.path.join(sub_dir, hash)


# models
class ModelStageStorage(BaseModel):
    stage_name: str
    files: List[str]
    mAP: float
    timestamp: int

    @root_validator(pre=True)
    def check_values(cls, values: dict) -> dict:
        if (not values['stage_name'] or not values['files'] or not values['timestamp'] or values['mAP'] < 0
                or values['mAP'] > 1):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"ModelStageStorage check failed with args: {values}")
        return values


class ModelStorage(BaseModel):
    executor_config: Dict[str, Any]
    task_context: Dict[str, Any]
    stages: Dict[str, ModelStageStorage]
    best_stage_name: str

    @root_validator(pre=True)
    def check_values(cls, values: dict) -> dict:
        if (not values.get('stages') or not values.get('best_stage_name') or not values.get('executor_config')
                or 'class_names' not in values.get('executor_config', {}) or not values.get('task_context')):
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"ModelStorage check failed with args: {values}")
        return values

    @property
    def class_names(self) -> List[str]:
        return self.executor_config['class_names']

    def get_model_meta(self, model_hash: str) -> mirpb.ModelMeta:
        model_meta = mirpb.ModelMeta()
        json_format.ParseDict(
            {
                'mean_average_precision': self.stages[self.best_stage_name].mAP,
                'model_hash': model_hash,
                'stages': {k: v.dict()
                           for k, v in self.stages.items()},
                'best_stage_name': self.best_stage_name,
            }, model_meta)
        return model_meta


def parse_model_hash_stage(model_hash_stage: str) -> Tuple[str, str]:
    model_hash, stage_name = model_hash_stage.split('@')
    if not model_hash or not stage_name:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"invalid model hash stage: {model_hash_stage}")
    return (model_hash, stage_name)


def prepare_model(model_location: str, model_hash: str, stage_name: str, dst_model_path: str) -> ModelStorage:
    """
    unpack model to `dst_model_path` and returns ModelStorage instance

    Args:
        model_location (str): model storage dir
        model_hash (str): hash of model package
        stage_name (str): model stage name, empty string to unpack all model files
        dst_model_path (str): path to destination model directory

    Raises:
        MirRuntimeError: if dst_model_path is not a directory
        MirRuntimeError: if model not found
        MirRuntimeError: if model package is invalid (lacks params, json or config file)

    Returns:
        ModelStorage
    """
    tar_file_path = os.path.join(model_location, model_hash)
    if not os.path.isfile(tar_file_path):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"tar_file is not a file: {tar_file_path}")

    os.makedirs(dst_model_path, exist_ok=True)

    logging.info(f"extracting models: {tar_file_path}, stage: {stage_name}")
    with tarfile.open(tar_file_path, 'r') as tar_file:
        # get model_stage of this package
        tar_file.extract('ymir-info.yaml', dst_model_path)
        with open(os.path.join(dst_model_path, 'ymir-info.yaml'), 'r') as f:
            ymir_info_dict = yaml.safe_load(f.read())
        # TODO: HANDLE OLD MODEL FORMAT
        model_storage = ModelStorage.parse_obj(ymir_info_dict)

        files: List[str]
        if stage_name:
            files = model_storage.stages[stage_name].files
        else:
            files = list({f for v in model_storage.stages.values() for f in v.files})
        for file_name in files:
            logging.info(f"    extracting {file_name} -> {dst_model_path}")
            tar_file.extract(file_name, dst_model_path)

    return model_storage


def pack_and_copy_models(model_storage: ModelStorage, model_dir_path: str, model_location: str) -> str:
    """
    pack model, returns model hash of the new model package
    """
    logging.info(f"packing models: {model_dir_path} -> {model_location}")

    ymir_info_file_name = 'ymir-info.yaml'
    ymir_info_file_path = os.path.join(model_dir_path, ymir_info_file_name)
    with open(ymir_info_file_path, 'w') as f:
        yaml.safe_dump(model_storage.dict(), f)

    tar_file_path = os.path.join(model_dir_path, 'model.tar.gz')
    with tarfile.open(tar_file_path, 'w:gz') as tar_gz_f:
        # packing models
        for stage_name, stage in model_storage.stages.items():
            logging.info(f"  model stage: {stage_name}")
            for file_name in stage.files:
                file_path = os.path.join(model_dir_path, file_name)
                logging.info(f"    packing {file_path} -> {file_name}")
                tar_gz_f.add(file_path, file_name)

        # packing ymir-info.yaml
        logging.info(f"  packing {ymir_info_file_path} -> {ymir_info_file_name}")
        tar_gz_f.add(ymir_info_file_path, ymir_info_file_name)

    os.makedirs(model_location, exist_ok=True)
    model_hash = hash_utils.sha1sum_for_file(tar_file_path)
    shutil.copyfile(tar_file_path, os.path.join(model_location, model_hash))
    os.remove(tar_file_path)

    logging.info(f"pack success, model hash: {model_hash}, best_stage_name: {model_storage.best_stage_name}, "
                 f"mAP: {model_storage.stages[model_storage.best_stage_name].mAP}")

    return model_hash


def repo_dot_mir_path(mir_root: str) -> str:
    dir = os.path.join(mir_root, '.mir')
    os.makedirs(dir, exist_ok=True)
    return dir


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


class _EnvConfig(BaseModel):
    task_id: str = 'default-task'
    run_training: bool = False
    run_mining: bool = False
    run_infer: bool = False

    input: _EnvInputConfig = _EnvInputConfig()
    output: _EnvOutputConfig = _EnvOutputConfig()


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


def get_docker_executable(runtime: str) -> str:
    if runtime == 'nvidia':
        return 'nvidia-docker'
    return 'docker'
