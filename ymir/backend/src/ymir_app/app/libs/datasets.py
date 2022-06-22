from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Dict, Optional, List
import tempfile
import pathlib
from zipfile import BadZipFile

from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api.errors.errors import (
    DatasetNotFound,
    FailedtoCreateDataset,
)
from app.config import settings
from app.constants.state import ResultState
from app.utils.files import FailedToDownload, verify_import_path, prepare_imported_dataset_dir, InvalidFileStructure
from app.utils.ymir_viz import VizClient
from app.utils.ymir_controller import (
    ControllerClient,
    gen_user_hash,
    gen_repo_hash,
)
from common_utils.labels import UserLabels


def import_dataset_in_background(
    db: Session,
    controller_client: ControllerClient,
    dataset_import: schemas.DatasetImport,
    user_id: int,
    task_hash: str,
    dataset_id: int,
) -> None:
    try:
        _import_dataset(db, controller_client, dataset_import, user_id, task_hash)
    except (OSError, BadZipFile, FailedToDownload, FailedtoCreateDataset, DatasetNotFound, InvalidFileStructure):
        logger.exception("[import dataset] failed to import dataset")
        crud.dataset.update_state(db, dataset_id=dataset_id, new_state=ResultState.error)


def _import_dataset(
    db: Session,
    controller_client: ControllerClient,
    dataset_import: schemas.DatasetImport,
    user_id: int,
    task_hash: str,
) -> None:
    parameters = {}  # type: Dict[str, Any]
    if dataset_import.input_dataset_id is not None:
        dataset = crud.dataset.get(db, id=dataset_import.input_dataset_id)
        if not dataset:
            raise DatasetNotFound()
        parameters = {
            "src_user_id": gen_user_hash(dataset.user_id),
            "src_repo_id": gen_repo_hash(dataset.project_id),
            "src_resource_id": dataset.hash,
            "strategy": dataset_import.strategy,
        }
    else:
        paths = ImportDatasetPaths(
            cache_dir=settings.SHARED_DATA_DIR, input_path=dataset_import.input_path, input_url=dataset_import.input_url
        )
        parameters = {
            "annotation_dir": paths.annotation_dir,
            "asset_dir": paths.asset_dir,
            "gt_dir": paths.gt_dir,
            "strategy": dataset_import.strategy,
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
        self.cache_dir = cache_dir
        self.input_url = input_url
        self.input_path = input_path
        self._data_dir: Optional[str] = None

    @property
    def annotation_dir(self) -> str:
        return str(self.data_dir / "annotations")

    @property
    def asset_dir(self) -> str:
        return str(self.data_dir / "images")

    @property
    def gt_dir(self) -> Optional[str]:
        gt_dir = self.data_dir / "gt"
        if not gt_dir.is_dir():
            return None
        return str(gt_dir)

    @property
    def data_dir(self) -> pathlib.Path:
        if not self._data_dir:
            if self.input_path:
                verify_import_path(self.input_path)
                self._data_dir = self.input_path
            elif self.input_url:
                temp_dir = tempfile.mkdtemp(prefix="import_dataset_", dir=self.cache_dir)
                self._data_dir = prepare_imported_dataset_dir(self.input_url, temp_dir)
            else:
                raise ValueError("input_path or input_url is required")
        return pathlib.Path(self._data_dir)


def evaluate_dataset(
    viz: VizClient,
    confidence_threshold: float,
    iou_threshold: float,
    require_average_iou: bool,
    need_pr_curve: bool,
    dataset_hash: str,
) -> Dict:
    if require_average_iou:
        # special placeholder for average iou
        iou_threshold = -1
    return viz.get_fast_evaluation(dataset_hash, confidence_threshold, iou_threshold, need_pr_curve)


def evaluate_datasets(
    viz: VizClient,
    user_id: int,
    project_id: int,
    user_labels: UserLabels,
    confidence_threshold: float,
    iou_threshold: float,
    require_average_iou: bool,
    need_pr_curve: bool,
    datasets: List[models.Dataset],
) -> Dict:
    dataset_id_mapping = {dataset.hash: dataset.id for dataset in datasets}
    viz.initialize(user_id=user_id, project_id=project_id, user_labels=user_labels)

    f_evaluate = partial(evaluate_dataset, viz, confidence_threshold, iou_threshold, require_average_iou, need_pr_curve)
    with ThreadPoolExecutor() as executor:
        res = executor.map(f_evaluate, dataset_id_mapping.keys())

    evaluations = ChainMap(*res)

    return {dataset_id_mapping[hash_]: evaluation for hash_, evaluation in evaluations.items()}
