from dataclasses import asdict, dataclass, field
import logging
import os
import pathlib
import requests
import shutil
import tarfile
from typing import Any, Dict, List, Optional, Union

from PIL import Image, UnidentifiedImageError
import yaml

from mir import scm
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


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


@dataclass
class ModelStorage:
    models: List[str] = field(default_factory=list)
    executor_config: Dict[str, Any] = field(default_factory=dict)
    task_context: Dict[str, Any] = field(default_factory=dict)
    class_names: List[str] = field(init=False)

    def __post_init__(self) -> None:
        self.class_names = self.executor_config.get('class_names', [])
        # check valid
        if not self.models or not self.executor_config or not self.task_context or not self.class_names:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_FILE,
                                  error_message='ModelStorage invalid: not enough infomations')

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def prepare_model(model_location: str, model_hash: str, dst_model_path: str) -> ModelStorage:
    """
    unpack model to `dst_model_path`

    Args:
        model_location (str): model storage dir
        model_hash (str): hash to model package
        dst_model_path (str): path to destination model directory

    Returns:
        ModelStorage: rel path to params, json, weights file and config file (start from dest_root)
    """
    model_id_rel_paths = store_assets_to_dir(asset_ids=[model_hash],
                                             out_root=dst_model_path,
                                             sub_folder='.',
                                             asset_location=model_location,
                                             create_prefix=False,
                                             need_suffix=False)
    model_file = os.path.join(dst_model_path, model_id_rel_paths[model_hash])
    model_storage = _unpack_models(tar_file=model_file, dest_root=dst_model_path)
    os.remove(model_file)
    return model_storage


def _unpack_models(tar_file: str, dest_root: str) -> ModelStorage:
    """
    unpack model to dest root directory

    Args:
        tar_file (str): path to model package
        dest_root (str): destination save directory

    Raises:
        MirRuntimeError: if dest_root is not a directory
        MirRuntimeError: if tar_file is not a file
        MirRuntimeError: if model package is invalid (lacks params, json or config file)

    Returns:
        ModelStorage: model names (start from dest_root), executor config and task context
    """
    if not os.path.isdir(dest_root):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"dest_root is not a directory: {dest_root}")
    if not os.path.isfile(tar_file):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"tar_file is not a file: {tar_file}")

    # params_file, json_file, weights_file, config_file = '', '', '', ''
    logging.info(f"extracting models from {tar_file}")
    with tarfile.open(tar_file, 'r') as tar_gz:
        for item in tar_gz:
            logging.info(f"extracting {item} -> {dest_root}")
            tar_gz.extract(item, dest_root)

    with open(os.path.join(dest_root, 'ymir-info.yaml'), 'r') as f:
        ymir_info_dict = yaml.safe_load(f.read())
    model_storage = ModelStorage(models=ymir_info_dict.get('models', []),
                                 executor_config=ymir_info_dict.get('executor_config', {}),
                                 task_context=ymir_info_dict.get('task_context', {}))

    return model_storage
