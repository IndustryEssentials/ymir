import enum
import pathlib
import random
import tempfile
from operator import attrgetter
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
    DuplicateDatasetError,
    FailedtoCreateDataset,
    FieldValidationFailed,
    NoDatasetPermission,
    FailedtoCreateTask,
    DatasetGroupNotFound,
)
from app.config import settings
from app.constants.state import ResultState
from app.constants.state import TaskState, TaskType
from app.schemas.dataset import MergeStrategy
from app.utils.files import FailedToDownload, is_valid_import_path, prepare_dataset
from app.utils.ymir_controller import (
    ControllerClient,
    gen_task_hash,
    gen_user_hash,
    gen_repo_hash,
)
from app.utils.ymir_viz import VizClient
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


@router.get(
    "/",
    response_model=schemas.DatasetPaginationOut,
)
def list_datasets(
    db: Session = Depends(deps.get_db),
    name: str = Query(None, description="search by dataset's name"),
    type_: TaskType = Query(None, alias="type", description="type of related task"),
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
        name=name,
        project_id=project_id,
        group_id=group_id,
        type_=type_,
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
def create_dataset(
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
    if crud.dataset_group.is_duplicated_name(db, user_id=current_user.id, name=dataset_import.dataset_group_name):
        raise DuplicateDatasetError()

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
        name=dataset_import.dataset_group_name,
        user_id=current_user.id,
        project_id=dataset_import.project_id,
    )
    logger.info(
        "[import dataset] created dataset_group(%s) for dataset",
        dataset_group.id,
    )
    dataset_in = schemas.DatasetCreate(
        name=f"{dataset_import.dataset_group_name}_initial",
        hash=task.hash,
        dataset_group_id=dataset_group.id,
        project_id=dataset_import.project_id,
        user_id=current_user.id,
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
    except (BadZipFile, FailedToDownload, FailedtoCreateDataset, DatasetNotFound):
        logger.exception("[create dataset] failed to import dataset")
        crud.dataset.update_state(db, dataset_id=dataset_id, new_state=ResultState.error)


def _import_dataset(
    db: Session,
    controller_client: ControllerClient,
    dataset_import: schemas.DatasetImport,
    user_id: int,
    task_hash: str,
) -> None:
    parameters = {}  # type: Dict[str, Any]
    if dataset_import.input_url is not None:
        # Controller will read this directory later
        # so temp_dir will not be removed here
        temp_dir = tempfile.mkdtemp(prefix="import_dataset_", dir=settings.SHARED_DATA_DIR)
        paths = prepare_dataset(dataset_import.input_url, temp_dir)
        if "annotations" not in paths or "images" not in paths:
            raise FailedtoCreateDataset()
        parameters = {
            "annotation_dir": str(paths["annotations"]),
            "asset_dir": str(paths["images"]),
            "strategy": dataset_import.strategy,
        }
    elif dataset_import.input_path is not None:
        src_path = pathlib.Path(dataset_import.input_path)
        if not is_valid_import_path(src_path):
            raise FailedtoCreateDataset()
        parameters = {
            "annotation_dir": str(src_path / "annotations"),
            "asset_dir": str(src_path / "images"),
            "strategy": dataset_import.strategy,
        }
    elif dataset_import.input_dataset_id is not None:
        dataset = crud.dataset.get(db, id=dataset_import.input_dataset_id)
        if not dataset:
            raise DatasetNotFound()
        parameters = {
            "src_user_id": gen_user_hash(dataset.user_id),
            "src_repo_id": gen_repo_hash(dataset.project_id),
            "src_resource_id": dataset.hash,
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
    except ValueError as e:
        # todo parse error message
        logger.exception("[create dataset] controller error: %s", e)
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
    dataset = crud.dataset.soft_remove(db, id=dataset_id)
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


@router.patch(
    "/{dataset_id}",
    response_model=schemas.DatasetOut,
    responses={404: {"description": "Dataset Not Found"}},
)
def update_dataset_name(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    dataset_in: schemas.DatasetUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update dataset name
    """
    if not dataset_in.name:
        raise FieldValidationFailed()

    dataset = crud.dataset.get_by_user_and_name(db, user_id=current_user.id, name=dataset_in.name)
    if dataset:
        raise DuplicateDatasetError()

    dataset = crud.dataset.get(db, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()
    dataset = crud.dataset.update(db, db_obj=dataset, obj_in=dataset_in)
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
    keyword_id: Optional[int] = Query(None),
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
        "keywords": assets.keywords,
        "items": assets.items,
        "total": assets.total,
        "negative_info": assets.negative_info,
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
    if assets.total == 0:
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
        include_class_ids=user_labels.get_class_ids(task_in.include_labels),
        exclude_class_ids=user_labels.get_class_ids(task_in.exclude_labels),
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
    task_hash = gen_task_hash(current_user.id, task_in.project_id)

    parameters = fusion_normalize_parameters(db, task_in, user_labels)
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

    # TODO(chao): data fusion parameter is different from other task, need save
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
        name=task.hash,
        hash=task.hash,
        dataset_group_id=task_in.dataset_group_id,
        project_id=task.project_id,
        user_id=task.user_id,
        task_id=task.id,
    )
    dataset = crud.dataset.create_with_version(db, obj_in=dataset_in, dest_group_name=dataset_group.name)
    logger.info("[create dataset] dataset record created: %s", dataset.name)

    return {"result": dataset}
