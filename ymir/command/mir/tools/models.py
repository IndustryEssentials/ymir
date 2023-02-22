from enum import IntEnum
import logging
import os
from pydantic import BaseModel, Field, root_validator
import shutil
import tarfile
from typing import Any, Dict, List, Tuple

from google.protobuf import json_format
import yaml

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.mir_storage import sha1sum_for_file
from mir.tools.model_updater import update_model_info
from mir.protos import mir_command_pb2 as mirpb
from mir.version import check_model_version_or_crash


class ModelObjectType(IntEnum):
    MOT_UNKNOWN = mirpb.ObjectType.OT_UNKNOWN
    MOT_DET_BOX = mirpb.ObjectType.OT_DET_BOX,
    MOT_SEM_SEG = mirpb.ObjectType.OT_SEG,
    MOT_INS_SEG = 4


class ModelStageStorage(BaseModel):
    stage_name: str
    files: List[str]
    timestamp: int

    # available in detection models
    mAP: float = Field(default=0, ge=0, le=1)
    mAR: float = Field(default=0, ge=0, le=1)

    # available in semantic segmentation models
    mIoU: float = Field(default=0, ge=0, le=1)
    mAcc: float = Field(default=0, ge=0, le=1)

    # available in instance segmentation models
    maskAP: float = Field(default=0, ge=0, le=1)
    boxAP: float = Field(default=0, ge=0, le=1)

    # available in detection / semantic segmentation / instance segmentation models
    tp: int = Field(default=0, ge=0)
    fp: int = Field(default=0, ge=0)
    fn: int = Field(default=0, ge=0)


class ModelStorage(BaseModel):
    executor_config: Dict[str, Any]
    task_context: Dict[str, Any]
    stages: Dict[str, ModelStageStorage]
    best_stage_name: str
    model_hash: str = ''
    stage_name: str = ''
    attachments: Dict[str, List[str]] = {}
    evaluate_config: Dict[str, float] = {}
    object_type: int = ModelObjectType.MOT_UNKNOWN.value
    package_version: str = Field(..., min_length=1)

    @root_validator
    def validate_model_storage(cls, values: dict) -> dict:
        check_model_version_or_crash(values['package_version'])
        if values.get('object_type', ModelObjectType.MOT_UNKNOWN) == ModelObjectType.MOT_UNKNOWN:
            logging.warning("Unknown model object type, treat as detection models")
            values['object_type'] = ModelObjectType.MOT_DET_BOX.value

        return values

    @property
    def class_names(self) -> List[str]:
        return self.executor_config['class_names']

    def get_model_meta(self) -> mirpb.ModelMeta:
        model_meta = mirpb.ModelMeta()
        json_format.ParseDict(
            {
                'mAP': self.stages[self.best_stage_name].mAP,
                'mIoU': self.stages[self.best_stage_name].mIoU,
                'maskAP': self.stages[self.best_stage_name].maskAP,
                'model_hash': self.model_hash,
                'object_type': self.object_type,
                'stages': {
                    k: {
                        'stage_name': v.stage_name,
                        'files': v.files,
                        'timestamp': v.timestamp,
                        'ci_averaged_evaluation': {
                            'ap': v.mAP,  # detection models
                            'ar': v.mAR,
                            'iou': v.mIoU,  # semantic segmentation models
                            'acc': v.mAcc,
                            'maskAP': v.maskAP,  # instance segmentation models
                            'boxAP': v.boxAP,
                            'tp': v.tp,  # all models
                            'fp': v.fp,
                            'fn': v.fn,
                        }
                    }
                    for k, v in self.stages.items()
                },
                'best_stage_name': self.best_stage_name,
                'class_names': self.class_names,
                'evaluate_config': {
                    'iou_thrs_interval': f"{self.evaluate_config.get('iou_thr', '')}",
                    'conf_thr': self.evaluate_config.get('conf_thr', 0),
                },
            }, model_meta)
        return model_meta


def parse_model_hash_stage(model_hash_stage: str) -> Tuple[str, str]:
    """
    parse model hash and stage name from string: `model_hash@stage_name`
    """
    components = model_hash_stage.split('@')
    model_hash = ''
    stage_name = ''
    if len(components) == 2:
        model_hash, stage_name = components
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
    if not model_location or not model_hash:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty model_location or model_hash')
    tar_file_path = os.path.join(model_location, model_hash)
    if not os.path.isfile(tar_file_path):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"tar_file is not a file: {tar_file_path}")

    os.makedirs(dst_model_path, exist_ok=True)

    logging.info(f"extracting models: {tar_file_path}, stage: {stage_name}")
    with tarfile.open(tar_file_path, 'r') as tar_file:
        # read and update model info
        tar_file.extract('ymir-info.yaml', dst_model_path)

        model_info_path = os.path.join(dst_model_path, 'ymir-info.yaml')
        update_model_info(model_info_path)
        with open(model_info_path, 'r') as f:
            ymir_info_dict = yaml.safe_load(f.read())

        model_storage = ModelStorage.parse_obj(ymir_info_dict)
        model_storage.model_hash = model_hash
        model_storage.stage_name = stage_name

        # extract model_stage files
        stage_and_file_names = []
        tar_file_names = set(tar_file.getnames())
        for file_name in model_storage.stages[stage_name].files:
            if file_name in tar_file_names:
                stage_and_file_names.append(file_name)
            elif f"{stage_name}/{file_name}" in tar_file_names:
                stage_and_file_names.append(f"{stage_name}/{file_name}")
            else:
                raise MirRuntimeError(
                    error_code=MirCode.RC_CMD_INVALID_FILE,
                    error_message=f"Can not find file name: {file_name} in model package: {tar_file_path}")
        os.makedirs(os.path.join(dst_model_path, stage_name), exist_ok=True)
        for name in stage_and_file_names:
            tar_file.extract(name, dst_model_path)

    return model_storage


def pack_and_copy_models(model_storage: ModelStorage, model_dir_path: str, model_location: str) -> str:
    """
    pack model, returns model hash of the new model package
    """
    logging.info(f"packing models: {model_dir_path} -> {model_location}, stages: {model_storage.stages.keys()}")

    ymir_info_file_name = 'ymir-info.yaml'
    ymir_info_file_path = os.path.join(model_dir_path, ymir_info_file_name)
    with open(ymir_info_file_path, 'w') as f:
        yaml.safe_dump(model_storage.dict(), f)

    tar_file_path = os.path.join(model_dir_path, 'model.tar.gz')
    with tarfile.open(tar_file_path, 'w:gz') as tar_gz_f:
        # packing models
        for stage_name, stage in model_storage.stages.items():
            stage_dir = os.path.join(model_dir_path, stage_name)
            for file_name in stage.files:
                # find model file in `stage_dir`, and then `model_dir`
                # compatible with old docker images
                file_path = _find_model_file(model_dirs=[stage_dir, model_dir_path], file_name=file_name)
                tar_file_key = f"{stage_name}/{file_name}"
                tar_gz_f.add(file_path, tar_file_key)

        # packing attachments
        for section, file_names in model_storage.attachments.items():
            section_dir = os.path.join(model_dir_path, 'attachments', section)
            for file_name in file_names:
                file_path = os.path.join(section_dir, file_name)
                tar_file_key = f"attachments/{section}/{file_name}"
                tar_gz_f.add(file_path, tar_file_key)

        # packing ymir-info.yaml
        tar_gz_f.add(ymir_info_file_path, ymir_info_file_name)

    os.makedirs(model_location, exist_ok=True)
    model_hash = sha1sum_for_file(tar_file_path)
    shutil.copyfile(tar_file_path, os.path.join(model_location, model_hash))
    os.remove(tar_file_path)

    logging.info(f"Pack success, model hash: {model_hash}, "
                 f"best stage: {model_storage.stages[model_storage.best_stage_name]}")

    model_storage.model_hash = model_hash
    return model_hash


def _find_model_file(model_dirs: List[str], file_name: str) -> str:
    for model_dir in model_dirs:
        file_path = os.path.join(model_dir, file_name)
        if os.path.isfile(file_path):
            return file_path
    raise FileNotFoundError(f"File not found: {file_name} in following dirs: {model_dirs}")
