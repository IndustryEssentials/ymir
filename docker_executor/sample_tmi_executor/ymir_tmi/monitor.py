import json
import logging
import time
import traceback
from typing import Dict, List, Tuple

from pydantic import BaseModel
import yaml

from ymir_tmi import env


def write_logger(info: str, percent: float = None, state: int = None, exception: Exception = None) -> None:
    logging.info(info)

    if percent is not None:
        _write_monitor_file(info, percent, state, exception)


def _write_monitor_file(info: str, percent: float = None, state: int = None, exception: Exception = None) -> None:
    env_config = env.get_current_env()
    with open(env_config.output.monitor_file, 'w') as f:
        f.write(f"{env_config.task_id}\t{time.time()}\t{percent}\t{state}\t{info}")
        f.write('\n')
        if exception:
            # ignore the last 2 items: write_logger and _write_monitor_file
            f.write(f"{''.join(traceback.format_stack()[:-2])}")


def write_training_result(model_names: List[str], mAP: float, classAPs: Dict[str, float], **kwargs) -> None:
    training_result = {
        'model': model_names,
        'map': mAP,
        'class_aps': classAPs,
    }
    training_result.update(kwargs)

    env_config = env.get_current_env()
    with open(env_config.output.training_result_file, 'w') as f:
        yaml.safe_dump(training_result, f)


def write_mining_result(mining_result: List[Tuple[str, float]]) -> None:
    env_config = env.get_current_env()
    with open(env_config.output.mining_result_file, 'w') as f:
        for asset_id, score in mining_result:
            f.write(f"{asset_id}\t{score}\n")


class Box(BaseModel):
    x: int
    y: int
    w: int
    h: int


class Annotation(BaseModel):
    class_name: str
    score: float
    box: Box


def write_infer_result(infer_result: Dict[str, List[Annotation]]) -> None:
    detection_result = {}
    for asset_id, annotations in infer_result.items():
        detection_result[asset_id] = {'annotations': [annotation.dict() for annotation in annotations]}

    result = {'detection': detection_result}
    env_config = env.get_current_env()
    with open(env_config.output.infer_result_file, 'w') as f:
        f.write(json.dumps(result))
