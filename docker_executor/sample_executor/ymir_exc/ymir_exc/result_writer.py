import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel
import yaml

from ymir_exc import env


_MAX_MODEL_STAGES_COUNT_ = 11  # 10 latest stages, 1 best stage


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
                      evaluation_result: Dict[str, Union[float, int]] = {},
                      timestamp: int = None,
                      attachments: Dict[str, List[str]] = None,
                      evaluate_config: Optional[dict] = None) -> None:
    """
    Write model stage and model attachments

    Args:
        stage_name (str): name to this model stage
        files (List[str]): model file NAMES for this stage
            All files should under directory: `/out/models` or `/out/models/<stage_name>`
        evaluation_result (Dict[str, Union[float, int]]): example: `{'mAP': 0.65}`
            evaluation result of this stage, it contains:
                for detection models:
                    mAP (float, required): mean average precision
                    mAR (float, optional): mean average recall
                for semantic segmentation models:
                    mIoU (float, required): mean IoU
                    mAcc (float, optional): mean accuracy
                for instance segmentation models:
                    maskAP (float, required): mean average precision for masks
                    boxAP (float, optional): mean average precision for boxes
                for all models:
                    tp (int, optional): true positive
                    fp (int, optional): false positive
                    fn (int, optional): false negative
        timestamp (int): timestamp (in seconds)
        evaluate_config (dict): configurations used to evaluate this model, which contains:
            iou_thr (float): iou threshold
            conf_thr (float): confidence threshold
    """
    if not stage_name or not files:
        raise ValueError('empty stage_name or files')
    if not stage_name.isidentifier():
        raise ValueError(
            f"invalid stage_name: {stage_name}, need alphabets, numbers and underlines, start with alphabets")

    training_result: dict = {}  # key: stage name, value: stage name, files, timestamp, mAP / mIoU / maskAP

    env_config = env.get_current_env()
    try:
        with open(env_config.output.training_result_file, 'r') as f:
            training_result = yaml.safe_load(stream=f)
    except FileNotFoundError:
        pass  # will create new if not exists, so dont care this exception

    model_stages = training_result.get('model_stages', {})

    model_stages[stage_name] = dict(
        stage_name=stage_name,
        files=files,
        timestamp=timestamp or int(time.time()),
        **evaluation_result,
    )

    main_metric_key = None
    metric_keys = ['maskAP', 'mIoU', 'mAP']
    for k in metric_keys:
        if k in evaluation_result:
            main_metric_key = k
            break
    if not main_metric_key:
        raise ValueError(f"Can not find compare key in evaluation_result, (should be one of {metric_keys})")

    # best stage
    sorted_model_stages = sorted(model_stages.values(),
                                 key=lambda x: (x.get(main_metric_key, 0), x.get('timestamp', 0)))
    training_result['best_stage_name'] = sorted_model_stages[-1]['stage_name']
    training_result[main_metric_key] = sorted_model_stages[-1][main_metric_key]

    # if too many stages, remove a earlest one
    if len(model_stages) > _MAX_MODEL_STAGES_COUNT_:
        sorted_model_stages = sorted(model_stages.values(), key=lambda x: x.get('timestamp', 0))
        del_stage_name = sorted_model_stages[0]['stage_name']
        if del_stage_name == training_result['best_stage_name']:
            del_stage_name = sorted_model_stages[1]['stage_name']
        del model_stages[del_stage_name]
        logging.info(f"data_writer removed model stage: {del_stage_name}")
    training_result['model_stages'] = model_stages

    # attachments
    training_result['attachments'] = attachments or {}

    # evaluate config
    if evaluate_config:
        training_result['evaluate_config'] = evaluate_config

    training_result['object_type'] = env.get_manifest_object_type()

    # save all
    with open(env_config.output.training_result_file, 'w') as f:
        yaml.safe_dump(data=training_result, stream=f)


def write_training_result(model_names: List[str], mAP: float, classAPs: Dict[str, float], **kwargs: dict) -> None:
    write_model_stage(stage_name='default_best_stage', files=model_names, evaluation_result={'mAP': mAP})


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
        detection_result[asset_basename] = {'boxes': [annotation.dict() for annotation in annotations]}

    result = {'detection': detection_result}
    env_config = env.get_current_env()
    with open(env_config.output.infer_result_file, 'w') as f:
        f.write(json.dumps(result))
