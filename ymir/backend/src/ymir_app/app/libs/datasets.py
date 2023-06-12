from typing import Any, Dict, List, Optional

from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api.errors.errors import (
    ControllerError,
    DatasetNotFound,
    FailedtoCreateDataset,
    FieldValidationFailed,
    PrematureDatasets,
)
from app.constants.state import ResultState, TaskState
from app.utils.ymir_controller import ControllerClient
from app.schemas.common import ImportStrategy
from id_definition.error_codes import APIErrorCode as error_codes
from id_definition.task_id import gen_repo_hash, gen_user_hash


def import_dataset_in_background(
    db: Session,
    controller_client: ControllerClient,
    dataset_import: schemas.DatasetImport,
    user_id: int,
    task_hash: str,
    object_type: int,
    dataset_id: int,
) -> None:
    try:
        _import_dataset(db, controller_client, dataset_import, user_id, task_hash, object_type)
    except DatasetNotFound:
        logger.exception("[import dataset] source dataset not found, could not copy")
        state_code = error_codes.DATASET_NOT_FOUND
    except FailedtoCreateDataset:
        logger.exception("[import dataset] controller error")
        state_code = error_codes.CONTROLLER_ERROR
    except FieldValidationFailed as e:
        logger.exception("[import dataset] missing input_path or input_url for import dataset(%s)", dataset_id)
        state_code = e.code
    except ControllerError as e:
        logger.exception(f"[import dataset] controller: {e.message}")
        state_code = e.code
    except Exception:
        logger.exception("[import dataset] failed to import dataset")
        state_code = error_codes.DATASET_FAILED_TO_IMPORT
    else:
        logger.info("[import dataset] successfully triggered import dataset(%s)", dataset_id)
        return

    task = crud.task.get_by_hash(db, task_hash)
    if task:
        crud.task.update_state(db, task=task, new_state=TaskState.error, state_code=str(state_code.value))
    crud.dataset.update_state(db, dataset_id=dataset_id, new_state=ResultState.error)


def _import_dataset(
    db: Session,
    controller_client: ControllerClient,
    dataset_import: schemas.DatasetImport,
    user_id: int,
    task_hash: str,
    object_type: int,
) -> None:
    parameters = {}  # type: Dict[str, Any]
    if dataset_import.input_dataset_id is not None:
        dataset = crud.dataset.get(db, id=dataset_import.input_dataset_id)
        if not dataset:
            raise DatasetNotFound()
        if object_type == dataset.object_type:
            annotation_strategy = dataset_import.strategy
        else:
            annotation_strategy = ImportStrategy.no_annotations
        parameters = {
            "src_user_id": gen_user_hash(dataset.user_id),
            "src_repo_id": gen_repo_hash(dataset.project_id),
            "src_resource_id": dataset.hash,
            "strategy": annotation_strategy,
            "object_type": object_type,
            "clean_dirs": True,
        }
    elif dataset_import.input_path or dataset_import.input_url:
        input_source = dataset_import.input_path or dataset_import.input_url
        parameters = {
            "asset_dir": input_source,
            "strategy": dataset_import.strategy,
            "object_type": object_type,
            "clean_dirs": dataset_import.input_path is None,  # for path importing, DO NOT clean_dirs
        }
    else:
        raise FieldValidationFailed()

    try:
        controller_client.import_dataset(
            user_id,
            dataset_import.project_id,
            task_hash,
            dataset_import.import_type,
            parameters,
        )
    except ValueError:
        logger.exception("[import dataset] controller error")
        raise FailedtoCreateDataset()


def ensure_datasets_are_ready(
    db: Session, *, user_id: Optional[int] = None, dataset_ids: List[int]
) -> List[models.Dataset]:
    dataset_ids = list(set(dataset_ids))
    if user_id:
        datasets = crud.dataset.get_multi_by_user_and_ids(db, user_id=user_id, ids=dataset_ids)
    else:
        datasets = crud.dataset.get_multi_by_ids(db, ids=dataset_ids)
    if len(dataset_ids) != len(datasets):
        raise DatasetNotFound()

    if not all(dataset.result_state == ResultState.ready for dataset in datasets):
        raise PrematureDatasets()
    return datasets
