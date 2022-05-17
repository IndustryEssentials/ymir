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
    ModelNotFound,
)
from app.config import settings
from app.utils.files import FailedToDownload, save_files
from app.utils.ymir_controller import ControllerClient

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
) -> Any:
    """
    Call Inference
    """
    model = crud.model.get(db, id=inference_in.model_id)
    if not model:
        logger.error("Failed to find model id: %s", inference_in.model_id)
        raise ModelNotFound()

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
            model.project_id,
            model.hash,
            asset_dir,
            docker_image.url,
            json.dumps(inference_in.docker_image_config),
        )
    except ValueError as e:
        logger.exception("Failed to call inference via Controller: %s", e)
        raise FailedToCallInference()

    result = {
        "model_id": inference_in.model_id,
        "annotations": extract_inference_annotations(resp, filename_mapping=filename_mapping),
    }
    return {"result": result}


def extract_inference_annotations(
    resp: Dict, *, inference_type: str = "detection", filename_mapping: Dict
) -> Generator:
    for filename, annotations in resp[inference_type]["image_annotations"].items():
        yield {
            "image_url": filename_mapping[filename],
            "detection": annotations["annotations"],
        }
