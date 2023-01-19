import os
import time
from typing import Callable, List

import yaml

from mir.protos import mir_command_pb2 as mirpb
from mir.version import DEFAULT_YMIR_SRC_VERSION, YMIR_MODEL_VERSION, ymir_salient_version


_ModelUpdaterType = Callable[[str], None]


def update_model_info(model_info_path: str) -> None:
    """
    Update an extracted model in `extracted_model_dir` to latest model version
    """
    # get model package version
    with open(os.path.join(model_info_path), 'r') as f:
        ymir_info_dict: dict = yaml.safe_load(f.read())
    src_ver = ymir_info_dict.get('package_version', DEFAULT_YMIR_SRC_VERSION)

    # get steps and update
    steps = _get_steps(src_ver=src_ver, dst_ver=YMIR_MODEL_VERSION)
    for model_func in steps:
        model_func(model_info_path)


def _get_steps(src_ver: str, dst_ver: str) -> List[_ModelUpdaterType]:
    src_ver = ymir_salient_version(src_ver)
    _UPDATE_NODES: List[str] = ['1.1.0', '2.0.0']
    _UPDATE_FUNCS: List[_ModelUpdaterType] = [_update_model_110_200]
    return _UPDATE_FUNCS[_UPDATE_NODES.index(src_ver):_UPDATE_NODES.index(dst_ver)]


# protected: 1.1.0 -> 2.0.0
def _update_model_110_200(model_info_path: str) -> None:
    with open(os.path.join(model_info_path), 'r') as f:
        model_info_src: dict = yaml.safe_load(f.read())

    _check_model_110(model_info_src)

    # update ymir-info.yaml
    executor_config_dict = model_info_src.get('executor_config', {})
    task_context_dict = model_info_src.get('task_context', {})
    models_list = model_info_src['models']
    best_stage_name = 'default_best_stage'
    model_stage_dict = {
        best_stage_name: {
            'files': models_list,
            'mAP': task_context_dict.get('mAP', 0),
            'stage_name': best_stage_name,
            'timestamp': int(time.time()),
        }
    }
    model_info_dst = {
        'executor_config': executor_config_dict,
        'task_context': task_context_dict,
        'stages': model_stage_dict,
        'best_stage_name': best_stage_name,
        'object_type': mirpb.ObjectType.OT_DET_BOX,
        'package_version': '2.0.0',
    }

    # write back again
    with open(os.path.join(model_info_path), 'w') as f:
        yaml.safe_dump(model_info_dst, f)


def _check_model_110(ymir_info: dict) -> None:
    # executor_config: must be dict
    # # models: must be list
    executor_config = ymir_info['executor_config']
    models_list = ymir_info['models']
    if not executor_config or not isinstance(executor_config, dict) or not models_list or not isinstance(
            models_list, list):
        raise ValueError('Invalid ymir-info.yaml for model version 1.1.0')
