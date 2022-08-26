import json
from typing import Any, Dict, Generator

from fastapi import APIRouter, Depends
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    FailedToCallInference,
    FailedtoDownloadError,
    InvalidInferenceConfig,
    ModelStageNotFound,
)
from app.config import settings
from app.utils.files import FailedToDownload, save_files
from app.utils.ymir_controller import ControllerClient
from common_utils.labels import UserLabels

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.InferenceOut,
)
def call_inference(
    *,
    inference_in: schemas.InferenceCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Call Inference
    """
    model_stage = crud.model_stage.get(db, id=inference_in.model_stage_id)
    if not model_stage:
        logger.error("Failed to find model stage id: %s", inference_in.model_stage_id)
        raise ModelStageNotFound()

    docker_image = crud.docker_image.get_inference_docker_image(db, url=inference_in.docker_image)
    if not docker_image:
        logger.error("Failed to find inference model")
        raise InvalidInferenceConfig()

    try:
        asset_dir, filename_mapping = save_files(inference_in.image_urls, settings.SHARED_DATA_DIR)
    except FailedToDownload:
        logger.error("Failed to download user content: %s", inference_in.image_urls)
        raise FailedtoDownloadError()

    try:
        resp = controller_client.call_inference(
            current_user.id,
            inference_in.project_id,
            model_stage.model.hash,  # type: ignore
            model_stage.name,
            asset_dir,
            docker_image.url,
            json.dumps(inference_in.docker_image_config),
        )
    except ValueError as e:
        logger.exception("Failed to call inference via Controller: %s", e)
        raise FailedToCallInference()

    result = {
        "model_stage_id": inference_in.model_stage_id,
        "annotations": extract_inference_annotations(resp, filename_mapping=filename_mapping, user_labels=user_labels),
    }
    return {"result": result}


def extract_inference_annotations(
    resp: Dict, *, inference_type: str = "detection", filename_mapping: Dict, user_labels: UserLabels
) -> Generator:
    for filename, annotations in resp[inference_type]["image_annotations"].items():
        annotations["annotations"]["class_name"] = user_labels.get_main_name(annotations["annotations"]["class_id"])
        yield {
            "image_url": filename_mapping[filename],
            "detection": annotations["annotations"],
        }
