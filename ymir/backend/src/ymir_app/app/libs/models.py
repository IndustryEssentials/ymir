import tempfile
import os
from typing import Dict, Any

from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api.errors.errors import (
    ModelNotFound,
    FailedtoImportModel,
    TaskNotFound,
    FieldValidationFailed,
)
from app.constants.state import ResultState, TaskType
from app.utils.files import NGINX_DATA_PATH, save_file, FailedToDownload
from app.utils.ymir_controller import gen_user_hash, gen_repo_hash, ControllerClient
from app.config import settings


def import_model_in_background(
    db: Session,
    controller_client: ControllerClient,
    model_import: schemas.ModelImport,
    user_id: int,
    task_hash: str,
    model_id: int,
) -> None:
    try:
        _import_model(db, controller_client, model_import, user_id, task_hash)
    except (
        ValueError,
        OSError,
        FieldValidationFailed,
        FailedtoImportModel,
        ModelNotFound,
        TaskNotFound,
        FailedToDownload,
    ):
        logger.exception("[import model] failed to import model, set model result_state to error")
        crud.model.update_state(db, model_id=model_id, new_state=ResultState.error)


def _import_model(
    db: Session, controller_client: ControllerClient, model_import: schemas.ModelImport, user_id: int, task_hash: str
) -> None:
    logger.info(
        "[import model] start importing model file from %s",
        model_import,
    )
    parameters: Dict[str, Any] = {}
    if model_import.import_type == TaskType.copy_model:
        # get the task.hash from input_model
        model_obj = crud.model.get(db, id=model_import.input_model_id)
        if model_obj is None:
            raise ModelNotFound()
        task_obj = crud.task.get(db, id=model_obj.task_id)
        if task_obj is None:
            raise TaskNotFound()
        parameters = {
            "src_user_id": gen_user_hash(model_obj.user_id),
            "src_repo_id": gen_repo_hash(model_obj.project_id),
            "src_resource_id": task_obj.hash,
        }
    elif model_import.import_type == TaskType.import_model and model_import.input_model_path is not None:
        # TODO(chao): remove model file after importing
        parameters = {
            "model_package_path": os.path.join(NGINX_DATA_PATH, model_import.input_model_path),
        }
    elif model_import.input_url:
        temp_dir = tempfile.mkdtemp(prefix="import_model_", dir=settings.SHARED_DATA_DIR)
        model_path = save_file(model_import.input_url, temp_dir)
        parameters = {"model_package_path": str(model_path)}
    else:
        raise FieldValidationFailed()

    try:
        controller_client.import_model(
            user_id=user_id,
            project_id=model_import.project_id,
            task_id=task_hash,
            task_type=model_import.import_type,
            args=parameters,
        )
    except ValueError as e:
        logger.exception("[import model] controller error: %s", e)
        raise FailedtoImportModel()
