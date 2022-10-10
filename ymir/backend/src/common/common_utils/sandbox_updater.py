import logging
import os
import shutil
from typing import Callable, List, Optional, Tuple

import yaml

from common_utils.sandbox_util import detect_users_and_repos
from common_utils.version import ymir_salient_version

from update_1_1_0_to_1_3_0.step_updater import update_models as update_models_110_130
from update_1_1_0_to_1_3_0.step_updater import update_repo as update_repo_110_130
from update_1_2_2_to_1_3_0.step_updater import update_models as update_models_122_130
from update_1_2_2_to_1_3_0.step_updater import update_repo as update_repo_122_130


_RepoUpdaterType = Callable[[str, str, str], None]
_ModelsUpdaterType = Callable[[str], None]
_StepUpdaterType = Tuple[Optional[_RepoUpdaterType], Optional[_ModelsUpdaterType]]


def update(sandbox_root: str, assets_root: str, models_root: str, src_ver: str, dst_ver: str) -> None:
    steps = _get_update_steps(src_ver=src_ver, dst_ver=dst_ver)
    if not steps:
        logging.info(f"nothing to update {src_ver} -> {dst_ver}")
        return

    _backup(sandbox_root=sandbox_root, models_root=models_root)

    # update
    user_to_repos = detect_users_and_repos(sandbox_root)
    try:
        for repo_func, models_func in steps:
            # update user repos
            if repo_func:
                for user_id, repo_ids in user_to_repos.items():
                    for repo_id in repo_ids:
                        repo_func(os.path.join(sandbox_root, user_id, repo_id), assets_root, models_root)
            # update models
            if models_func:
                models_func(models_root)

        for user_id in user_to_repos:
            _update_user_labels(label_path=os.path.join(sandbox_root, user_id, 'labels.yaml'), dst_ver=dst_ver)
    except Exception as e:
        _roll_back(sandbox_root=sandbox_root, models_root=models_root)
        raise e

    # cleanup
    shutil.rmtree(os.path.join(sandbox_root, 'sandbox-bk'))
    shutil.rmtree(os.path.join(sandbox_root, 'ymir-models-bk'))


def _backup(sandbox_root: str, models_root: str) -> None:
    # user dirs in sandbox_root
    sandbox_backup_dir = os.path.join(sandbox_root, 'sandbox-bk')
    os.makedirs(sandbox_backup_dir, exist_ok=False)
    for user_id in detect_users_and_repos(sandbox_root):
        shutil.copytree(src=os.path.join(sandbox_root, user_id),
                        dst=os.path.join(sandbox_backup_dir, user_id),
                        symlinks=True)

    models_backup_dir = os.path.join(sandbox_root, 'ymir-models-bk')
    shutil.copytree(src=models_root, dst=models_backup_dir)


def _roll_back(sandbox_root: str, models_root: str) -> None:
    sandbox_backup_dir = os.path.join(sandbox_root, 'sandbox-bk')
    for user_id in detect_users_and_repos(sandbox_root):
        src_user_dir = os.path.join(sandbox_backup_dir, user_id)
        dst_user_dir = os.path.join(sandbox_root, user_id)
        shutil.rmtree(dst_user_dir)
        shutil.move(src=src_user_dir, dst=dst_user_dir)

    # models_root
    models_backup_dir = os.path.join(sandbox_root, 'ymir-models-bk')
    for model_hash in os.listdir(models_backup_dir):
        src_model_path = os.path.join(models_backup_dir, model_hash)
        if not os.path.isfile(src_model_path):
            continue
        dst_model_path = os.path.join(models_root, model_hash)
        os.remove(dst_model_path)
        shutil.move(src=src_model_path, dst=dst_model_path)

    shutil.rmtree(sandbox_backup_dir)
    shutil.rmtree(models_backup_dir)
    logging.info('roll back done')


def _get_update_steps(src_ver: str, dst_ver: str) -> List[_StepUpdaterType]:
    eq_src_ver = ymir_salient_version(src_ver)
    eq_dst_ver = ymir_salient_version(dst_ver)

    # _UPDATE_NODES: List[str] = ['1.1.0', '1.3.0']
    # _UPDATE_FUNCS: List[_StepUpdaterType] = [(update_repo_110_130, update_models_110_130)]
    _UPDATE_NODES: List[str] = ['1.2.2', '1.3.0']
    _UPDATE_FUNCS: List[_StepUpdaterType] = [(update_repo_122_130, update_models_122_130)]
    return _UPDATE_FUNCS[_UPDATE_NODES.index(eq_src_ver):_UPDATE_NODES.index(eq_dst_ver)]


def _update_user_labels(label_path: str, dst_ver: str) -> None:
    logging.info(f"updating user labels: {label_path}, 110 -> 130")

    # todo: uncomment this
    # with open(label_path, 'r') as f:
    #     label_contents = yaml.safe_load(f)
    # label_contents['ymir_version'] = dst_ver
    # with open(label_path, 'w') as f:
    #     yaml.safe_dump(label_contents, f)
