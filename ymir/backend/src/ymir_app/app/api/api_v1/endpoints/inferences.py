import os
import json
from typing import Any, Dict, Generator, Tuple

from fastapi import APIRouter, Depends
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.errors.errors import (
    FailedToCallInference,
    FailedtoDownloadError,
    InvalidInferenceConfig,
    InvalidInferenceResultFormat,
    ModelStageNotFound,
    ProjectNotFound,
)
from app.config import settings
from app.utils.files import FailedToDownload, save_file, save_files
from app.utils.ymir_controller import ControllerClient

router = APIRouter()


@router.post("/", response_model=schemas.InferenceOut)
def call_inference(
    *,
    inference_in: schemas.InferenceCreate,
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Call Inference
    """
    if inference_in.model_stage_id:
        model_stage = crud.model_stage.get(db, id=inference_in.model_stage_id)
        if not model_stage:
            logger.error("Failed to find model stage id: %s", inference_in.model_stage_id)
            raise ModelStageNotFound()
        model_hash, model_stage_name = model_stage.model.hash, model_stage.name
    else:
        # FIXME
        #  adhoc use pre-defined multimodal model
        model_hash, model_stage_name = adhoc_prepare_multimodal_model()

    docker_image = crud.docker_image.get_inference_docker_image(db, id=inference_in.docker_image_id)
    if not docker_image:
        logger.error("Failed to find inference model")
        raise InvalidInferenceConfig()

    project = crud.project.get_by_user_and_id(db, user_id=current_user.id, id=inference_in.project_id)
    if not project:
        raise ProjectNotFound()

    try:
        asset_dir, filename_mapping = save_files(inference_in.image_urls, settings.SHARED_DATA_DIR, keep=True)
    except (FailedToDownload, FileNotFoundError):
        logger.error("Failed to get user provided images: %s", inference_in.image_urls)
        raise FailedtoDownloadError()

    try:
        resp = controller_client.call_inference(
            current_user.id,
            project.id,
            project.object_type,
            model_hash,
            model_stage_name,
            asset_dir,
            docker_image.url,
            json.dumps(inference_in.docker_image_config),
        )
    except ValueError as e:
        logger.exception("Failed to call inference via Controller: %s", e)
        raise FailedToCallInference()

    try:
        annotations = list(extract_inference_annotations(resp, filename_mapping=filename_mapping))
    except KeyError:
        logger.exception("Invalid inference result format: %s", resp)
        raise InvalidInferenceResultFormat()
    return {"result": {"annotations": annotations}}


def extract_inference_annotations(resp: Dict, *, filename_mapping: Dict) -> Generator:
    for filename, annotations in resp["objects"]["image_annotations"].items():
        annotations = annotations["boxes"]  # FIXME ad hoc
        yield {
            "image_url": filename_mapping[filename],
            "annotations": annotations,
        }


def adhoc_prepare_multimodal_model() -> Tuple[str, str]:
    model_hash, model_stage_name = settings.MULTIMODAL_MODEL_HASH, "default"
    if settings.MODELS_PATH and not os.path.isfile(f"{settings.MODELS_PATH}/{model_hash}"):
        save_file(f"http://web/{model_hash}", settings.MODELS_PATH, keep=True)
        logger.info(f"downloaded pre-defined multimodal model {model_hash}")
    return model_hash, model_stage_name
