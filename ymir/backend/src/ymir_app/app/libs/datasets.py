from typing import Any, Dict, Optional, List
import tempfile
import pathlib
from zipfile import BadZipFile

from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api.errors.errors import (
    ControllerError,
    DatasetNotFound,
    FailedtoCreateDataset,
    PrematureDatasets,
)
from app.config import settings
from app.constants.state import ResultState, TaskState
from app.utils.files import FailedToDownload, locate_import_paths, prepare_downloaded_paths, InvalidFileStructure
from app.utils.ymir_controller import ControllerClient, gen_user_hash, gen_repo_hash
from app.schemas.common import ImportStrategy
from id_definition.error_codes import APIErrorCode as error_codes


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
        return _import_dataset(db, controller_client, dataset_import, user_id, task_hash, object_type)
    except FailedToDownload:
        logger.exception("[import dataset] failed to download dataset file")
        state_code = error_codes.FAILED_TO_DOWNLOAD
    except (InvalidFileStructure, FileNotFoundError):
        logger.exception("[import dataset] invalid dataset file structure")
        state_code = error_codes.INVALID_DATASET_STRUCTURE
    except DatasetNotFound:
        logger.exception("[import dataset] source dataset not found, could not copy")
        state_code = error_codes.DATASET_NOT_FOUND
    except FailedtoCreateDataset:
        logger.exception("[import dataset] controller error")
        state_code = error_codes.CONTROLLER_ERROR
    except BadZipFile:
        logger.exception("[import dataset] invalid zip file")
        state_code = error_codes.INVALID_DATASET_ZIP_FILE
    except ControllerError as e:
        logger.exception(f"[import dataset] controller: {e.message}")
        state_code = e.code
    except Exception:
        logger.exception("[import dataset] failed to import dataset")
        state_code = error_codes.DATASET_FAILED_TO_IMPORT

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
    else:
        paths = ImportDatasetPaths(
            cache_dir=settings.SHARED_DATA_DIR, input_path=dataset_import.input_path, input_url=dataset_import.input_url
        )
        parameters = {
            "asset_dir": paths.asset_dir,
            "gt_dir": paths.gt_dir,
            "strategy": dataset_import.strategy,
            "object_type": object_type,
            "clean_dirs": dataset_import.input_path is None,  # for path importing, DO NOT clean_dirs
        }

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


class ImportDatasetPaths:
    def __init__(
        self, input_path: Optional[str], input_url: Optional[str], cache_dir: str = settings.SHARED_DATA_DIR
    ) -> None:
        self._asset_path: Optional[pathlib.Path] = None
        self._gt_path: Optional[pathlib.Path] = None
        self._pred_path: Optional[pathlib.Path] = None

        if input_path:
            self._asset_path, self._gt_path, self._pred_path = locate_import_paths(input_path)
        elif input_url:
            temp_dir = tempfile.mkdtemp(prefix="import_dataset_", dir=cache_dir)
            self._asset_path, self._gt_path, self._pred_path = prepare_downloaded_paths(input_url, temp_dir)
        else:
            raise ValueError("input_path or input_url is required")

    @property
    def asset_dir(self) -> str:
        return str(self._asset_path)

    @property
    def gt_dir(self) -> Optional[str]:
        return str(self._gt_path) if self._gt_path else None

    @property
    def pred_dir(self) -> Optional[str]:
        return str(self._pred_path) if self._pred_path else None


def ensure_datasets_are_ready(db: Session, dataset_ids: List[int]) -> List[models.Dataset]:
    dataset_ids = list(set(dataset_ids))
    datasets = crud.dataset.get_multi_by_ids(db, ids=dataset_ids)
    if len(dataset_ids) != len(datasets):
        raise DatasetNotFound()

    if not all(dataset.result_state == ResultState.ready for dataset in datasets):
        raise PrematureDatasets()
    return datasets
