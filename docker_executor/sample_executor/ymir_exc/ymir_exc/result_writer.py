import json
import os
import time
from typing import Dict, List, Tuple

from pydantic import BaseModel
import yaml

from ymir_exc import env

_MAX_MODEL_STAGES_COUNT_ = 10


class Box(BaseModel):
    x: int
    y: int
    w: int
    h: int


class Annotation(BaseModel):
    class_name: str
    score: float
    box: Box


def write_training_result(model_names: List[str], mAP: float, classAPs: Dict[str, float], **kwargs: dict) -> None:
    training_result = {
        'model': model_names,
        'map': mAP,
        'class_aps': classAPs,
    }
    training_result.update(kwargs)

    env_config = env.get_current_env()
    with open(env_config.output.training_result_file, 'w') as f:
        yaml.safe_dump(training_result, f)


def write_model_stage(stage_name: str,
                      model_files: List[str],
                      mAP: float,
                      as_best: bool = False,
                      timestamp: int = None) -> None:
    if not stage_name or not model_files:
        raise ValueError('empty stage_name or model_files')

    training_result: dict = {}  # key: stage name, value: stage name, files, timestamp, mAP

    env_config = env.get_current_env()
    try:
        with open(env_config.output.training_result_file, 'r') as f:
            training_result = yaml.safe_load(stream=f)
    except FileNotFoundError:
        pass  # will create new if not exists, so dont care this exception

    model_stages = training_result.get('model_stages', {})
    if stage_name in model_stages:
        raise ValueError(f"stage_name: {stage_name} already exists")

    model_stages[stage_name] = {
        'stage_name': stage_name,
        'files': model_files,
        'timestamp': timestamp or time.time(),
        'mAP': mAP
    }
    if as_best:
        training_result['best_model_stage'] = stage_name

    # if too many stages, remove a smallest one
    sorted_model_stages = sorted(model_stages.values(), key=lambda x: x.get('timestamp', 0))
    best_model_stage = training_result.get('best_model_stage', '')
    if len(model_stages) > _MAX_MODEL_STAGES_COUNT_:
        del_stage_name = sorted_model_stages[0]['stage_name']
        if del_stage_name == best_model_stage:
            del_stage_name = sorted_model_stages[1]['stage_name']
        del model_stages[del_stage_name]
    training_result['model_stages'] = model_stages

    # best stage and best map
    if not best_model_stage:
        training_result['best_model_stage'] = sorted_model_stages[-1]['stage_name']
    training_result['map'] = model_stages[training_result['best_model_stage']]['mAP']

    # save all
    with open(env_config.output.training_result_file, 'w') as f:
        yaml.safe_dump(data=training_result, stream=f)


def write_mining_result(mining_result: List[Tuple[str, float]]) -> None:
    # sort desc by score
    sorted_mining_result = sorted(mining_result, reverse=True, key=(lambda v: v[1]))

    env_config = env.get_current_env()
    with open(env_config.output.mining_result_file, 'w') as f:
        for asset_id, score in sorted_mining_result:
            f.write(f"{asset_id}\t{score}\n")


def write_infer_result(infer_result: Dict[str, List[Annotation]]) -> None:
    detection_result = {}
    for asset_path, annotations in infer_result.items():
        asset_basename = os.path.basename(asset_path)
        detection_result[asset_basename] = {'annotations': [annotation.dict() for annotation in annotations]}

    result = {'detection': detection_result}
    env_config = env.get_current_env()
    with open(env_config.output.infer_result_file, 'w') as f:
        f.write(json.dumps(result))
