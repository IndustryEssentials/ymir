import logging
import os
from pydantic import BaseModel, Field
import shutil
import tarfile
from typing import Any, Dict, List, Tuple

from google.protobuf import json_format
import yaml

from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.mir_storage import sha1sum_for_file
from mir.protos import mir_command_pb2 as mirpb


class ModelStageStorage(BaseModel):
    stage_name: str
    files: List[str]
    mAP: float = Field(..., ge=0, le=1)
    timestamp: int


class ModelStorage(BaseModel):
    executor_config: Dict[str, Any]
    task_context: Dict[str, Any]
    stages: Dict[str, ModelStageStorage]
    best_stage_name: str
    model_hash: str = ''
    stage_name: str = ''
    attachments: Dict[str, Any] = {}

    @property
    def class_names(self) -> List[str]:
        return self.executor_config['class_names']

    def get_model_meta(self) -> mirpb.ModelMeta:
        model_meta = mirpb.ModelMeta()
        json_format.ParseDict(
            {
                'mean_average_precision': self.stages[self.best_stage_name].mAP,
                'model_hash': self.model_hash,
                'stages': {k: v.dict()
                           for k, v in self.stages.items()},
                'best_stage_name': self.best_stage_name,
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

    logging.info(f"extracting models: {tar_file_path}, stage: {stage_name or '(all)'}")
    with tarfile.open(tar_file_path, 'r') as tar_file:
        # get model_stage of this package
        tar_file.extract('ymir-info.yaml', dst_model_path)
        with open(os.path.join(dst_model_path, 'ymir-info.yaml'), 'r') as f:
            ymir_info_dict = yaml.safe_load(f.read())
        # TODO: HANDLE OLD MODEL FORMAT
        model_storage = ModelStorage.parse_obj(ymir_info_dict)
        model_storage.model_hash = model_hash
        model_storage.stage_name = stage_name

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

        # packing attachments:sampled_images
        for image_name in model_storage.attachments.get('sampled_images', []):
            image_path = os.path.join(model_dir_path, image_name)
            logging.info(f"    packing {image_path} -> {image_name}")
            tar_gz_f.add(image_path, image_name)

        # packing ymir-info.yaml
        logging.info(f"  packing {ymir_info_file_path} -> {ymir_info_file_name}")
        tar_gz_f.add(ymir_info_file_path, ymir_info_file_name)

    os.makedirs(model_location, exist_ok=True)
    model_hash = sha1sum_for_file(tar_file_path)
    shutil.copyfile(tar_file_path, os.path.join(model_location, model_hash))
    os.remove(tar_file_path)

    logging.info(f"pack success, model hash: {model_hash}, best_stage_name: {model_storage.best_stage_name}, "
                 f"mAP: {model_storage.stages[model_storage.best_stage_name].mAP}")

    model_storage.model_hash = model_hash
    return model_hash
