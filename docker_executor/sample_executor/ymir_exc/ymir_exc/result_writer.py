import json
import logging
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


def write_model_stage(stage_name: str,
                      files: List[str],
                      mAP: float,
                      as_best: bool = False,
                      timestamp: int = None) -> None:
    if not stage_name or not files:
        raise ValueError('empty stage_name or files')
    if not stage_name.isidentifier():
        raise ValueError(
            f"invalid stage_name: {stage_name}, need alphabets, numbers and underlines, start with alphabets")

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
        'files': files,
        'timestamp': timestamp or int(time.time()),
        'mAP': mAP
    }

    if as_best:
        training_result['__user_defined_best_stage_name'] = stage_name

    training_result['best_stage_name'] = training_result.get('__user_defined_best_stage_name', stage_name)
    training_result['map'] = model_stages[training_result['best_stage_name']]['mAP']

    # if too many stages, remove a smallest one
    if len(model_stages) > _MAX_MODEL_STAGES_COUNT_:
        sorted_model_stages = sorted(model_stages.values(), key=lambda x: x.get('timestamp', 0))
        del_stage_name = sorted_model_stages[0]['stage_name']
        if del_stage_name == training_result.get('best_model_stage', ''):
            del_stage_name = sorted_model_stages[1]['stage_name']
        del model_stages[del_stage_name]
        logging.info(f"data_writer removed model stage: {del_stage_name}")
    training_result['model_stages'] = model_stages

    # save all
    with open(env_config.output.training_result_file, 'w') as f:
        yaml.safe_dump(data=training_result, stream=f)


def write_training_result(model_names: List[str], mAP: float, classAPs: Dict[str, float], **kwargs: dict) -> None:
    write_model_stage(stage_name='default_stage', files=model_names, mAP=mAP)


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
