from operator import attrgetter
import enum
import random
from typing import Any, Dict, Optional, List

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
    NoDatasetPermission,
    FailedtoCreateTask,
    FailedToHideProtectedResources,
    DatasetGroupNotFound,
    ProjectNotFound,
    MissingOperations,
    RefuseToProcessMixedOperations,
    DatasetsNotInSameGroup,
)
from app.config import settings
from app.constants.state import TaskState, TaskType, ResultState
from app.utils.iteration import get_iteration_context_converter
from app.utils.ymir_controller import ControllerClient, gen_task_hash
from app.utils.ymir_viz import VizClient
from app.schemas.dataset import MergeStrategy
from app.libs.datasets import import_dataset_in_background, evaluate_dataset
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


@router.post(
    "/batch",
    response_model=schemas.DatasetsOut,
)
def batch_update_datasets(
    *,
    db: Session = Depends(deps.get_db),
    dataset_ops: schemas.BatchOperations,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if not dataset_ops.operations:
        raise MissingOperations()
    project = crud.project.get(db, dataset_ops.project_id)
    if not project:
        raise ProjectNotFound()
    to_process = {op.id_ for op in dataset_ops.operations}
    if to_process.intersection(project.referenced_dataset_ids):
        raise FailedToHideProtectedResources()
    actions = {op.action for op in dataset_ops.operations}
    if len(actions) != 1:
        # for now, we do not support mixed operations, for example,
        #  hide and unhide in a single batch request
        raise RefuseToProcessMixedOperations()

    datasets = crud.dataset.batch_toggle_visibility(db, ids=list(to_process), action=list(actions)[0])
    return {"result": datasets}


class SortField(enum.Enum):
    id = "id"
    create_datetime = "create_datetime"
    update_datetime = "update_datetime"
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
    visible: bool = Query(True),
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
        visible=visible,
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


@router.post(
    "/evaluation",
    response_model=schemas.dataset.DatasetEvaluationOut,
)
def evaluate_datasets(
    *,
    db: Session = Depends(deps.get_db),
    evaluation_in: schemas.dataset.DatasetEvaluationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    viz_client: VizClient = Depends(deps.get_viz_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    evaluate dataset against ground truth
    """
    gt_dataset = crud.dataset.get(db, id=evaluation_in.gt_dataset_id)
    other_datasets = crud.dataset.get_multi_by_ids(db, ids=evaluation_in.other_dataset_ids)
    if not gt_dataset or len(evaluation_in.other_dataset_ids) != len(other_datasets):
        raise DatasetNotFound()
    if not is_same_group([gt_dataset, *other_datasets]):
        # confine evaluation to the same dataset group
        raise DatasetsNotInSameGroup()

    evaluations = evaluate_dataset(
        controller_client,
        viz_client,
        current_user.id,
        evaluation_in.project_id,
        user_labels,
        evaluation_in.confidence_threshold,
        gt_dataset,
        other_datasets,
    )
    return {"result": evaluations}


def is_same_group(datasets: List[models.Dataset]) -> bool:
    return len({dataset.dataset_group_id for dataset in datasets}) == 1
