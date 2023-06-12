from typing import Dict

import grpc
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api.errors.errors import ModelNotFound, TaskNotFound, FieldValidationFailed
from app.constants.state import ResultState, TaskState
from app.utils.ymir_controller import ControllerClient
from id_definition.error_codes import APIErrorCode as error_codes


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
    except (grpc.RpcError, ValueError):
        logger.exception("[import model] controller error for importing model(%s)", model_id)
        state_code = error_codes.CONTROLLER_ERROR
    except FieldValidationFailed as e:
        logger.exception("[import model] invalid parameter for importing model(%s)", model_id)
        state_code = e.code
    except (ModelNotFound, TaskNotFound):
        logger.exception("[import model] source model not found for copy model(%s)", model_id)
        state_code = error_codes.MODEL_NOT_FOUND
    except Exception:
        state_code = error_codes.FAILED_TO_IMPORT_MODEL
        logger.exception("[import model] failed to download for importing model(%s)", model_id)
    else:
        logger.info("[import model] successfully triggered import model(%s)", model_id)
        return

    task = crud.task.get_by_hash(db, task_hash)
    if not task:  # make mypy happy
        return
    # Set task state to error upon any exceptions
    crud.task.update_state(db, task=task, new_state=TaskState.error, state_code=str(state_code.value))
    crud.model.update_state(db, model_id=model_id, new_state=ResultState.error)


def _import_model(
    db: Session, controller_client: ControllerClient, model_import: schemas.ModelImport, user_id: int, task_hash: str
) -> None:
    logger.info("[import model] start importing model file from %s", model_import)
    parameters = model_import.get_import_parameters(db)
    logger.info("[import model] importing model parameters: %s", parameters)
    controller_client.import_model(
        user_id=user_id,
        project_id=model_import.project_id,
        task_id=task_hash,
        task_type=model_import.import_type,
        args=parameters,
    )


def create_model_stages(db: Session, model_id: int, model_info: Dict) -> None:
    stages_in = [
        schemas.ModelStageCreate(
            name=stage_name,
            metrics=stage_info["ci_averaged_evaluation"],
            timestamp=stage_info["timestamp"],
            model_id=model_id,
        )
        for stage_name, stage_info in model_info["model_stages"].items()
    ]
    crud.model_stage.batch_create(db, objs_in=stages_in)
    crud.model.update_recommonded_stage_by_name(db, model_id=model_id, stage_name=model_info["best_stage_name"])
