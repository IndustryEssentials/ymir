import logging
import os
import pathlib
import requests
import shutil
from typing import Dict, List, Optional, Union

from PIL import Image, UnidentifiedImageError

from mir import scm


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
        raise ValueError("invalid git: needs str or CmdScm")

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
        raise ValueError("invalid git: needs str or CmdScm")

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
        raise ValueError("invalid out_root")
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
            sub_sub_folder_rel = sub_folder

        if need_suffix:
            try:
                asset_image = Image.open(assets_location[asset_id])
                file_format = asset_image.format.lower()
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
        raise ValueError(f"Invalid src, not a abs path: {src}")


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
        raise ValueError("asset_location is not set.")

    return {id: os.path.join(asset_location, id) for id in asset_ids}
