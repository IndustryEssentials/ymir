from functools import wraps
import linecache
import logging
import os
import pathlib
import time
import requests
import shutil
import tarfile
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, root_validator
import yaml

from mir import scm
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


# Store assets in asset_ids to out_root/sub_folder,
# return relative path to the out_root, staring with sub_folder.
# Set overwrite to False to avoid overwriting.
def store_assets_to_dir(asset_ids: List[str],
                        out_root: str,
                        sub_folder: str,
                        asset_location: str,
                        overwrite: bool = False,
                        create_prefix: bool = True,
                        need_suffix: bool = True) -> Dict[str, str]:
    """
    load assets in location and save them to destination local folder
    Args:
        asset_ids: a list of asset ids (asset hashes)
        out_root: the root of output path
        sub_folder: sub folder to the output path, if no sub, set to '.'
        asset_location: server location prefix of assets, if set to none, try to read it from mir repo config
        overwrite (bool): if True, still copy assets even if assets already exists in export dir
        create_prefix (bool): use last 2 chars of asset id as a sub dir
    """
    # if out_root exists, but not a folder, raise error
    if os.path.exists(out_root) and not os.path.isdir(out_root):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="invalid out_root")
    os.makedirs(out_root, exist_ok=True)
    sub_dir_abs = os.path.join(out_root, sub_folder)
    os.makedirs(sub_dir_abs, exist_ok=True)

    assets_location = _get_assets_location(asset_ids, asset_location)

    unknown_format_count = 0
    total_count = len(asset_ids)
    asset_id_to_rel_paths: Dict[str, str] = {}
    for idx, asset_id in enumerate(asset_ids):
        if create_prefix:
            suffix = asset_id[-2:]
            sub_sub_folder_abs = os.path.join(sub_dir_abs, suffix)
            os.makedirs(sub_sub_folder_abs, exist_ok=True)
            sub_sub_folder_rel = os.path.join(sub_folder, suffix)
        else:
            sub_sub_folder_abs = sub_dir_abs
            sub_sub_folder_rel = sub_folder.strip("./")

        if need_suffix:
            try:
                asset_image = Image.open(assets_location[asset_id])
                file_format = asset_image.format.lower()  # type: ignore
            except UnidentifiedImageError:
                file_format = 'unknown'
                unknown_format_count += 1

        file_name = (f"{asset_id}.{file_format.lower()}" if need_suffix else asset_id)
        asset_path_abs = os.path.join(sub_sub_folder_abs, file_name)  # path started from out_root
        asset_path_rel = os.path.join(sub_sub_folder_rel, file_name)  # path started from sub_folder
        _store_asset_to_location(assets_location[asset_id], asset_path_abs, overwrite=overwrite)
        asset_id_to_rel_paths[asset_id] = asset_path_rel

        if idx > 0 and idx % 5000 == 0:
            logging.info(f"exporting {idx} / {total_count} assets")

    if unknown_format_count > 0:
        logging.warning(f"unknown format asset count: {unknown_format_count}")

    return asset_id_to_rel_paths


def _store_asset_to_location(src: str, dst: str, overwrite: bool = False) -> None:
    if not src or not dst:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not overwrite and os.path.isfile(dst):
        return
    if src.startswith('http'):  # from http request
        response = requests.get(src)
        if len(response.content) > 0:
            with open(dst, "wb") as f:
                f.write(response.content)
    elif src.startswith('/'):  # from filesystem, require abs path.
        shutil.copyfile(src, dst)
    else:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"Invalid src, not a abs path: {src}")


def _get_assets_location(asset_ids: List[str], asset_location: str) -> Dict[str, str]:
    """
    get asset locations
    Args:
        asset_ids: a list of asset ids (asset hashes)
        asset_location: the server location of assets.
    Returns:
        a dict, key: asset id, value: asset location url
    Raises:
        Attribute exception if asset_location is not set, and can not be found in config file
    """

    # asset_location is a required field.
    # CMD layer should NOT aware where the asset is stored.
    if not asset_location:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="asset_location is not set.")

    return {id: os.path.join(asset_location, id) for id in asset_ids}


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


def get_docker_executable(gpu_ids: str) -> str:
    if gpu_ids:
        return 'nvidia-docker'

    return 'docker'
