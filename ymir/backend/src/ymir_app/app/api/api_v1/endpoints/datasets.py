from operator import attrgetter
import enum
import pathlib
import random
import tempfile
from typing import Any, Dict, Optional
from zipfile import BadZipFile

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    AssetNotFound,
    DatasetNotFound,
    DuplicateDatasetGroupError,
    FailedtoCreateDataset,
    NoDatasetPermission,
    FailedtoCreateTask,
    DatasetGroupNotFound,
)
from app.config import settings
from app.constants.state import TaskState, TaskType, ResultState
from app.utils.files import FailedToDownload, verify_import_path, prepare_imported_dataset_dir, InvalidFileStructure
from app.utils.iteration import get_iteration_context_converter
from app.utils.ymir_controller import (
    ControllerClient,
    gen_task_hash,
    gen_user_hash,
    gen_repo_hash,
)
from app.utils.ymir_viz import VizClient
from app.schemas.dataset import MergeStrategy
from common_utils.labels import UserLabels

router = APIRouter()


@router.get(
    "/batch",
    response_model=schemas.DatasetsOut,
)
def batch_get_datasets(
    db: Session = Depends(deps.get_db),
    dataset_ids: str = Query(None, example="1,2,3", alias="ids"),
) -> Any:
    ids = [int(i) for i in dataset_ids.split(",")]
    datasets = crud.dataset.get_multi_by_ids(db, ids=ids)
    if not datasets:
        raise DatasetNotFound()
    return {"result": datasets}


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"
    asset_count = "asset_count"
    source = "source"


@router.get(
    "/",
    response_model=schemas.DatasetPaginationOut,
)
def list_datasets(
    db: Session = Depends(deps.get_db),
    source: TaskType = Query(None, description="type of related task"),
    project_id: int = Query(None),
    group_id: int = Query(None),
    state: ResultState = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
    order_by: SortField = Query(SortField.id),
    is_desc: bool = Query(True),
    start_time: int = Query(None, description="from this timestamp"),
    end_time: int = Query(None, description="to this timestamp"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of datasets,
    pagination is supported by means of offset and limit
    """
    datasets, total = crud.dataset.get_multi_datasets(
        db,
        user_id=current_user.id,
        project_id=project_id,
        group_id=group_id,
        source=source,
        state=state,
        offset=offset,
        limit=limit,
        order_by=order_by.name,
        is_desc=is_desc,
        start_time=start_time,
        end_time=end_time,
    )
    return {"result": {"total": total, "items": datasets}}


@router.get(
    "/public",
    response_model=schemas.DatasetPaginationOut,
)
def get_public_datasets(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all the public datasets

    public datasets come from User set by env (PUBLIC_DATASET_OWNER)
    """
    datasets, total = crud.dataset.get_multi_datasets(
        db,
        user_id=settings.PUBLIC_DATASET_OWNER,
    )
    return {"result": {"total": total, "items": datasets}}


@router.post(
    "/importing",
    response_model=schemas.DatasetOut,
)
def import_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_import: schemas.DatasetImport,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create dataset.

    Three Import Strategy:
    - no_annotations = 1
    - ignore_unknown_annotations = 2
    - stop_upon_unknown_annotations = 3
    """
    # 1. check if dataset group name is available
    if crud.dataset_group.is_duplicated_name_in_project(
        db, project_id=dataset_import.project_id, name=dataset_import.group_name
    ):
        raise DuplicateDatasetGroupError()

    # 2. create placeholder task
    if dataset_import.input_dataset_id:
        # user has no access to other's datasets
        # save source dataset name beforehand
        src_dataset = crud.dataset.get(db, id=dataset_import.input_dataset_id)
        if src_dataset:
            dataset_import.input_dataset_name = src_dataset.name
    task = crud.task.create_placeholder(
        db,
        type_=dataset_import.import_type,  # type: ignore
        user_id=current_user.id,
        project_id=dataset_import.project_id,
        state_=TaskState.pending,
        parameters=dataset_import.json(),
    )
    logger.info("[import dataset] related task record created: %s", task.hash)

    # 3. create dataset record
    dataset_group = crud.dataset_group.create_dataset_group(
        db,
        name=dataset_import.group_name,
        user_id=current_user.id,
        project_id=dataset_import.project_id,
    )
    logger.info(
        "[import dataset] created dataset_group(%s) for dataset",
        dataset_group.id,
    )
    dataset_in = schemas.DatasetCreate(
        hash=task.hash,
        description=dataset_import.description,
        dataset_group_id=dataset_group.id,
        project_id=dataset_import.project_id,
        user_id=current_user.id,
        source=task.type,
        task_id=task.id,
    )
    dataset = crud.dataset.create_with_version(db, obj_in=dataset_in, dest_group_name=dataset_group.name)
    logger.info("[import dataset] dataset record created: %s", dataset.name)

    # 4. run background task
    background_tasks.add_task(
        import_dataset_in_background,
        db,
        controller_client,
        dataset_import,
        current_user.id,
        task.hash,
        dataset.id,
    )
    return {"result": dataset}


def import_dataset_in_background(
    db: Session,
    controller_client: ControllerClient,
    pre_dataset: schemas.DatasetImport,
    user_id: int,
    task_hash: str,
    dataset_id: int,
) -> None:
    try:
        _import_dataset(db, controller_client, pre_dataset, user_id, task_hash)
    except (BadZipFile, FailedToDownload, FailedtoCreateDataset, DatasetNotFound, InvalidFileStructure):
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


@router.delete(
    "/{dataset_id}",
    response_model=schemas.DatasetOut,
    responses={
        400: {"description": "No permission"},
        404: {"description": "Dataset Not Found"},
    },
)
def delete_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete dataset
    (soft delete actually)
    """
    dataset = crud.dataset.get(db, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()
    if dataset.user_id != current_user.id:
        raise NoDatasetPermission()
    dataset_group_id = dataset.dataset_group_id
    dataset = crud.dataset.soft_remove(db, id=dataset_id)

    # remove dataset group if all dataset is deleted
    _, total = crud.dataset.get_multi_datasets(
        db,
        user_id=current_user.id,
        group_id=dataset_group_id,
    )
    if not total:
        crud.dataset_group.soft_remove(db, id=dataset_group_id)

    return {"result": dataset}


@router.get(
    "/{dataset_id}",
    response_model=schemas.DatasetOut,
    responses={404: {"description": "Dataset Not Found"}},
)
def get_dataset(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get verbose information of specific dataset
    """
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()
    return {"result": dataset}


@router.get(
    "/{dataset_id}/assets",
    response_model=schemas.AssetPaginationOut,
    responses={404: {"description": "Dataset Not Found"}},
)
def get_assets_of_dataset(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    offset: int = 0,
    limit: int = settings.DEFAULT_LIMIT,
    keyword: Optional[str] = Query(None),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get asset list of specific dataset,
    pagination is supported by means of offset and limit
    """
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()

    keyword_id = user_labels.get_class_ids(keyword)[0] if keyword else None
    viz_client.initialize(
        user_id=current_user.id,
        project_id=dataset.project_id,
        branch_id=dataset.hash,
    )
    assets = viz_client.get_assets(
        keyword_id=keyword_id,
        limit=limit,
        offset=offset,
        user_labels=user_labels,
    )
    result = {
        "items": assets.items,
        "total": assets.total,
    }
    return {"result": result}


@router.get(
    "/{dataset_id}/assets/random",
    response_model=schemas.AssetOut,
    responses={404: {"description": "Asset Not Found"}},
)
def get_random_asset_id_of_dataset(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get random asset from specific dataset
    """
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()

    offset = get_random_asset_offset(dataset)
    viz_client.initialize(
        user_id=current_user.id,
        project_id=dataset.project_id,
        branch_id=dataset.hash,
    )
    assets = viz_client.get_assets(
        keyword_id=None,
        offset=offset,
        limit=1,
        user_labels=user_labels,
    )
    if len(assets.items) == 0:
        raise AssetNotFound()
    return {"result": assets.items[0]}


def get_random_asset_offset(dataset: models.Dataset) -> int:
    if not dataset.asset_count:
        raise AssetNotFound()
    offset = random.randint(0, dataset.asset_count - 1)
    return offset


@router.get(
    "/{dataset_id}/assets/{asset_hash}",
    response_model=schemas.AssetOut,
    responses={404: {"description": "Asset Not Found"}},
)
def get_asset_of_dataset(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    asset_hash: str = Path(..., description="in asset hash format"),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get asset from specific dataset
    """
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()

    viz_client.initialize(
        user_id=current_user.id,
        project_id=dataset.project_id,
        branch_id=dataset.hash,
    )
    asset = viz_client.get_asset(
        asset_id=asset_hash,
        user_labels=user_labels,
    )
    if not asset:
        raise AssetNotFound()
    return {"result": asset}


def fusion_normalize_parameters(
    db: Session,
    task_in: schemas.DatasetsFusionParameter,
    user_labels: UserLabels,
) -> Dict:
    include_datasets_info = crud.dataset.get_multi_by_ids(db, ids=[task_in.main_dataset_id] + task_in.include_datasets)

    include_datasets_info.sort(
        key=attrgetter("update_datetime"),
        reverse=(task_in.include_strategy == MergeStrategy.prefer_newest),
    )

    exclude_datasets_info = crud.dataset.get_multi_by_ids(db, ids=task_in.exclude_datasets)
    parameters = dict(
        include_datasets=[dataset_info.hash for dataset_info in include_datasets_info],
        include_strategy=task_in.include_strategy,
        exclude_datasets=[dataset_info.hash for dataset_info in exclude_datasets_info],
        include_class_ids=user_labels.get_class_ids(names_or_aliases=task_in.include_labels),
        exclude_class_ids=user_labels.get_class_ids(names_or_aliases=task_in.exclude_labels),
        sampling_count=task_in.sampling_count,
    )

    return parameters


@router.post(
    "/fusion",
    response_model=schemas.DatasetOut,
)
def create_dataset_fusion(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.DatasetsFusionParameter,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Create data fusion
    """
    logger.info(
        "[create task] create dataset fusion with payload: %s",
        jsonable_encoder(task_in),
    )

    with get_iteration_context_converter(db, user_labels) as iteration_context_converter:
        task_in_parameters = iteration_context_converter(task_in)

    parameters = fusion_normalize_parameters(db, task_in_parameters, user_labels)
    task_hash = gen_task_hash(current_user.id, task_in.project_id)

    try:
        resp = controller_client.create_data_fusion(
            current_user.id,
            task_in.project_id,
            task_hash,
            parameters,
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        raise FailedtoCreateTask()

    # 1. create task
    task = crud.task.create_placeholder(
        db,
        type_=TaskType.data_fusion,
        user_id=current_user.id,
        project_id=task_in.project_id,
        hash_=task_hash,
        state_=TaskState.pending,
        parameters=task_in.json(),
    )
    logger.info("[create dataset] related task record created: %s", task.hash)

    # 2. create dataset record
    dataset_group = crud.dataset_group.get(db, id=task_in.dataset_group_id)
    if not dataset_group:
        raise DatasetGroupNotFound()
    dataset_in = schemas.DatasetCreate(
        hash=task.hash,
        dataset_group_id=task_in.dataset_group_id,
        project_id=task.project_id,
        user_id=task.user_id,
        source=task.type,
        task_id=task.id,
    )
    dataset = crud.dataset.create_with_version(db, obj_in=dataset_in, dest_group_name=dataset_group.name)
    logger.info("[create dataset] dataset record created: %s", dataset.name)

    return {"result": dataset}


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
