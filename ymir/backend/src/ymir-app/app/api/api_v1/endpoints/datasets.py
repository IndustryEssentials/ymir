import enum
import pathlib
import random
import tempfile
from typing import Any, Dict, List, Optional
from zipfile import BadZipFile
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session
from app.utils.class_ids import convert_keywords_to_classes
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
)
from app.config import settings
from app.constants.state import TaskState, TaskType
from app.utils.class_ids import get_keyword_id_to_name_mapping
from app.utils.files import FailedToDownload, is_valid_import_path, prepare_dataset
from app.utils.ymir_controller import (
    ControllerClient,
    gen_task_hash,
    gen_user_hash,
    gen_repo_hash,
)
from app.utils.ymir_viz import VizClient

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
    state: TaskState = Query(None),
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
    Get all the public datasets,
    public datasets come from User 1
    """
    datasets, total = crud.dataset.get_multi_by_user(
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
    # 1. check if name is available
    if crud.dataset.is_duplicated_name(
        db, user_id=current_user.id, name=dataset_import.name
    ):
        raise DuplicateDatasetError()

    # 2. create task
    task_hash = gen_task_hash(current_user.id, dataset_import.project_id)
    task_in = schemas.TaskCreate(
        name=task_hash,
        type=dataset_import.import_type,
        project_id=dataset_import.project_id,
    )
    task = crud.task.create_task(
        db, obj_in=task_in, task_hash=task_hash, user_id=current_user.id
    )
    logger.info("[create dataset] related task record created: %s", task)

    # 3. create dataset record
    dataset_in = schemas.DatasetCreate(
        name=dataset_import.name,
        hash=task_hash,
        dataset_group_id=dataset_import.dataset_group_id,
        project_id=dataset_import.project_id,
        user_id=current_user.id,
        task_id=task.id,
    )
    dataset = crud.dataset.create_with_version(db, obj_in=dataset_in)
    logger.info("[create dataset] dataset record created: %s", dataset)

    # 4. run background task
    background_tasks.add_task(
        import_dataset_in_background,
        db,
        controller_client,
        dataset_import,
        current_user.id,
        task_hash,
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
    except (BadZipFile, FailedToDownload, FailedtoCreateDataset, DatasetNotFound) as e:
        logger.error("[create dataset] failed to import dataset: %s", e)
        crud.dataset.update_state(db, dataset_id=dataset_id, new_state=TaskState.error)


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
        temp_dir = tempfile.mkdtemp(
            prefix="import_dataset_", dir=settings.SHARED_DATA_DIR
        )
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
    dependencies=[Depends(deps.get_current_active_user)],
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
    dependencies=[Depends(deps.get_current_active_user)],
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
    dataset = crud.dataset.get_by_user_and_id(
        db, user_id=current_user.id, id=dataset_id
    )
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

    dataset = crud.dataset.get_by_user_and_name(
        db, user_id=current_user.id, name=dataset_in.name
    )
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
    labels: List[str] = Depends(deps.get_personal_labels),
) -> Any:
    """
    Get asset list of specific dataset,
    pagination is supported by means of offset and limit
    """
    dataset = crud.dataset.get_by_user_and_id(
        db, user_id=current_user.id, id=dataset_id
    )
    if not dataset:
        raise DatasetNotFound()

    keyword_id_to_name = get_keyword_id_to_name_mapping(labels)
    keyword_name_to_id = {v: k for k, v in keyword_id_to_name.items()}
    logger.info(
        "keyword_id_to_name: %s, keyword_name_to_id: %s",
        keyword_id_to_name,
        keyword_name_to_id,
    )

    keyword_id = keyword_id or keyword_name_to_id.get(keyword)

    viz_client.config(
        user_id=current_user.id,
        project_id=dataset.project_id,
        branch_id=dataset.hash,
        keyword_id_to_name=keyword_id_to_name,
    )
    assets = viz_client.get_assets(keyword_id=keyword_id, limit=limit, offset=offset)
    result = {
        "keywords": assets.keywords,
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
    labels: List[str] = Depends(deps.get_personal_labels),
) -> Any:
    """
    Get random asset from specific dataset
    """
    dataset = crud.dataset.get_by_user_and_id(
        db, user_id=current_user.id, id=dataset_id
    )
    if not dataset:
        raise DatasetNotFound()

    keyword_id_to_name = get_keyword_id_to_name_mapping(labels)
    offset = get_random_asset_offset(dataset)
    viz_client.config(
        user_id=current_user.id,
        project_id=dataset.project_id,
        branch_id=dataset.hash,
        keyword_id_to_name=keyword_id_to_name,
    )
    assets = viz_client.get_assets(keyword_id=None, offset=offset, limit=1)
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
    labels: List = Depends(deps.get_personal_labels),
) -> Any:
    """
    Get asset from specific dataset
    """
    dataset = crud.dataset.get_by_user_and_id(
        db, user_id=current_user.id, id=dataset_id
    )
    if not dataset:
        raise DatasetNotFound()

    keyword_id_to_name = get_keyword_id_to_name_mapping(labels)
    viz_client.config(
        user_id=current_user.id,
        project_id=dataset.project_id,
        branch_id=dataset.hash,
        keyword_id_to_name=keyword_id_to_name,
    )
    asset = viz_client.get_asset(asset_id=asset_hash)
    if not asset:
        raise AssetNotFound()
    return {"result": asset}


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
    labels: List[str] = Depends(deps.get_personal_labels),
) -> Any:
    """
    Create data fusion
    """
    logger.debug(
        "[create task] create dataset fusion with payload: %s",
        jsonable_encoder(task_in),
    )
    task_id = gen_task_hash(current_user.id, task_in.project_id)

    parameters = dict(
        include_datasets=[task_in.main_dataset_id] + task_in.include_datasets,
        include_strategy=task_in.include_strategy,
        exclude_datasets=task_in.exclude_datasets,
        include_class_ids=convert_keywords_to_classes(labels, task_in.include_labels),
        exclude_class_ids=convert_keywords_to_classes(labels, task_in.exclude_labels),
        sampling_count=task_in.sampling_count,
    )
    try:
        resp = controller_client.create_data_fusion(
            current_user.id,
            task_in.project_id,
            task_id,
            parameters,
        )
        logger.info("[create task] controller response: %s", resp)
    except ValueError:
        raise FailedtoCreateTask()

    # TODO(chao): data fusion parameter is diffrence from other task, need save
    task_info = schemas.TaskCreate(
        name=task_id,
        type=TaskType.data_fusion,
        project_id=task_in.project_id,
    )
    # 1. create task
    task = crud.task.create_task(
        db, obj_in=task_info, task_hash=task_id, user_id=current_user.id
    )

    # 2. create dataset record
    dataset_in = schemas.DatasetCreate(
        name=task.hash,
        hash=task.hash,
        dataset_group_id=task_in.dataset_group_id,
        project_id=task.project_id,
        user_id=task.user_id,
        task_id=task.id,
    )
    dataset = crud.dataset.create_with_version(db, obj_in=dataset_in)
    logger.info("[create dataset] dataset record created: %s", dataset)

    return {"result": dataset}
