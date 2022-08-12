from operator import attrgetter
import enum
import random
from typing import Any, Dict, Optional, List

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    AssetNotFound,
    ControllerError,
    DatasetNotFound,
    DuplicateDatasetGroupError,
    NoDatasetPermission,
    FailedToHideProtectedResources,
    DatasetGroupNotFound,
    ProjectNotFound,
    RequiredFieldMissing,
    MissingOperations,
    RefuseToProcessMixedOperations,
)
from app.config import settings
from app.constants.state import TaskState, TaskType, ResultState
from app.utils.iteration import get_iteration_context_converter
from app.utils.ymir_controller import ControllerClient, gen_task_hash
from app.utils.ymir_viz import VizClient
from app.schemas.dataset import MergeStrategy
from app.libs.datasets import import_dataset_in_background, evaluate_datasets, ensure_datasets_are_ready
from common_utils.labels import UserLabels

router = APIRouter()


@router.get("/batch", response_model=schemas.DatasetsOut)
def batch_get_datasets(
    db: Session = Depends(deps.get_db),
    dataset_ids: str = Query(None, example="1,2,3", alias="ids"),
) -> Any:
    ids = [int(i) for i in dataset_ids.split(",")]
    datasets = crud.dataset.get_multi_by_ids(db, ids=ids)
    if not datasets:
        raise DatasetNotFound()
    return {"result": datasets}


@router.get("/analysis", response_model=schemas.DatasetsAnalysesOut)
def get_datasets_analysis(
    db: Session = Depends(deps.get_db),
    viz_client: VizClient = Depends(deps.get_viz_client),
    project_id: int = Query(None),
    dataset_ids: str = Query(None, example="1,2,3", alias="ids"),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    ids = [int(i) for i in dataset_ids.split(",")]
    datasets = ensure_datasets_are_ready(db, dataset_ids=ids)

    viz_client.initialize(user_id=current_user.id, project_id=project_id, user_labels=user_labels)
    results = []
    for dataset in datasets:
        res = viz_client.get_dataset(dataset.hash)
        res.group_name = dataset.group_name  # type: ignore
        res.version_num = dataset.version_num  # type: ignore
        results.append(res)
    return {"result": {"datasets": results}}


@router.post("/batch", response_model=schemas.DatasetsOut)
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


@router.get("/", response_model=schemas.DatasetPaginationOut)
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


@router.get("/public", response_model=schemas.DatasetPaginationOut)
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


@router.post("/importing", response_model=schemas.DatasetOut)
def import_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_import: schemas.DatasetImport,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Import dataset.

    Three Import Strategy:
    - no_annotations = 1
    - ignore_unknown_annotations = 2
    - stop_upon_unknown_annotations = 3
    - add unknown annotations = 4
    """
    # 1. check if dataset group name is available
    logger.info("[import dataset] import dataset with payload: %s", dataset_import.json())
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


@router.get("/{dataset_id}/stats", response_model=schemas.dataset.DatasetStatsOut)
def get_dataset_stats(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    project_id: int = Query(None),
    keywords_str: str = Query(None, alias="keywords"),
    viz_client: VizClient = Depends(deps.get_viz_client),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()

    keywords = keywords_str.split(",")
    if not keywords:
        raise RequiredFieldMissing()

    keyword_ids = user_labels.get_class_ids(keywords)
    viz_client.initialize(
        user_id=current_user.id,
        project_id=project_id,
        branch_id=dataset.hash,
        user_labels=user_labels,
    )
    dataset_stats = viz_client.get_dataset_stats(keyword_ids=keyword_ids)
    return {"result": dataset_stats}


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
    keywords: Optional[List[str]] = Query(None),
    cm_types: Optional[List[str]] = Query(None),
    cks: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
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

    if keyword:
        keywords = [keyword]
    keyword_ids = user_labels.get_class_ids(keywords) if keywords else None

    viz_client.initialize(
        user_id=current_user.id,
        project_id=dataset.project_id,
        branch_id=dataset.hash,
        user_labels=user_labels,
        use_viewer=True,
    )
    assets = viz_client.get_assets(
        keyword_ids=keyword_ids,
        cm_types=cm_types,
        cks=cks,
        tags=tags,
        limit=limit,
        offset=offset,
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
        user_labels=user_labels,
    )
    assets = viz_client.get_assets(
        keyword_id=None,
        offset=offset,
        limit=1,
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
        user_labels=user_labels,
        use_viewer=True,
    )
    assets = viz_client.get_assets(asset_hash=asset_hash, limit=1)
    if assets.total != 1:
        raise AssetNotFound()
    return {"result": assets.items[0]}


def normalize_fusion_parameter(
    db: Session,
    fusion_params: schemas.DatasetsFusionParameter,
    user_labels: UserLabels,
) -> Dict:
    in_datasets = crud.dataset.get_multi_by_ids(
        db, ids=[fusion_params.main_dataset_id] + fusion_params.include_datasets
    )
    in_datasets.sort(
        key=attrgetter("create_datetime"),
        reverse=(fusion_params.include_strategy == MergeStrategy.prefer_newest),
    )
    ex_datasets = crud.dataset.get_multi_by_ids(db, ids=fusion_params.exclude_datasets)
    return {
        "include_datasets": [dataset.hash for dataset in in_datasets],
        "strategy": fusion_params.include_strategy,
        "exclude_datasets": [dataset.hash for dataset in ex_datasets],
        "include_class_ids": user_labels.get_class_ids(names_or_aliases=fusion_params.include_labels),
        "exclude_class_ids": user_labels.get_class_ids(names_or_aliases=fusion_params.exclude_labels),
        "sampling_count": fusion_params.sampling_count,
    }


@router.post("/fusion", response_model=schemas.DatasetOut)
def create_dataset_fusion(
    *,
    db: Session = Depends(deps.get_db),
    in_fusion: schemas.DatasetsFusionParameter,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Create data fusion
    """
    logger.info("[fusion] create dataset fusion with payload: %s", in_fusion.json())

    with get_iteration_context_converter(db, user_labels) as iteration_context_converter:
        fusion_params = iteration_context_converter(in_fusion)

    parameters = normalize_fusion_parameter(db, fusion_params, user_labels)
    task_hash = gen_task_hash(current_user.id, in_fusion.project_id)

    try:
        controller_client.create_data_fusion(
            current_user.id,
            in_fusion.project_id,
            task_hash,
            parameters,
        )
    except ValueError:
        logger.exception("[fusion] failed to create fusion via controller")
        raise ControllerError()

    task = crud.task.create_placeholder(
        db,
        type_=TaskType.data_fusion,
        user_id=current_user.id,
        project_id=in_fusion.project_id,
        hash_=task_hash,
        state_=TaskState.pending,
        parameters=in_fusion.json(),
    )
    logger.info("[fusion] related task record created: %s", task.hash)

    dataset_group = crud.dataset_group.get(db, id=in_fusion.dataset_group_id)
    if not dataset_group:
        raise DatasetGroupNotFound()
    fused_dataset = crud.dataset.create_as_task_result(db, task, dataset_group.id, description=in_fusion.description)
    logger.info("[fusion] dataset record created: %s", fused_dataset.name)

    return {"result": fused_dataset}


@router.post("/evaluation", response_model=schemas.dataset.DatasetEvaluationOut)
def batch_evaluate_datasets(
    *,
    db: Session = Depends(deps.get_db),
    evaluation_in: schemas.dataset.DatasetEvaluationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    viz_client: VizClient = Depends(deps.get_viz_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    evaluate datasets by themselves
    """
    logger.info("[evaluate] evaluate dataset with payload: %s", evaluation_in.json())
    datasets = crud.dataset.get_multi_by_ids(db, ids=evaluation_in.dataset_ids)
    if len(evaluation_in.dataset_ids) != len(datasets):
        raise DatasetNotFound()

    evaluations = evaluate_datasets(
        viz_client,
        current_user.id,
        evaluation_in.project_id,
        user_labels,
        evaluation_in.confidence_threshold,
        evaluation_in.iou_threshold,
        evaluation_in.require_average_iou,
        evaluation_in.need_pr_curve,
        datasets,
    )
    return {"result": evaluations}


@router.post("/check_duplication", response_model=schemas.dataset.DatasetCheckDuplicationOut)
def check_duplication(
    *,
    db: Session = Depends(deps.get_db),
    in_datasets: schemas.dataset.MultiDatasetsWithProjectID,
    current_user: models.User = Depends(deps.get_current_active_user),
    viz_client: VizClient = Depends(deps.get_viz_client),
) -> Any:
    """
    check duplication in two datasets
    """
    datasets = ensure_datasets_are_ready(db, dataset_ids=in_datasets.dataset_ids)

    viz_client.initialize(user_id=current_user.id, project_id=in_datasets.project_id)
    duplicated_asset_count = viz_client.check_duplication([dataset.hash for dataset in datasets])
    return {"result": duplicated_asset_count}


@router.post("/merge", response_model=schemas.dataset.DatasetOut)
def merge_datasets(
    *,
    db: Session = Depends(deps.get_db),
    in_merge: schemas.dataset.DatasetMergeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
) -> Any:
    """
    Merge multiple datasets
    """
    logger.info("[merge] merge dataset with payload: %s", in_merge.json())
    main_dataset = crud.dataset.get(db, id=in_merge.dataset_id)
    if not main_dataset:
        raise DatasetNotFound()

    if in_merge.include_datasets:
        in_datasets = ensure_datasets_are_ready(db, dataset_ids=[in_merge.dataset_id, *in_merge.include_datasets])
        in_datasets.sort(
            key=attrgetter("create_datetime"),
            reverse=(in_merge.merge_strategy == MergeStrategy.prefer_newest),
        )
    else:
        in_datasets = [main_dataset]

    ex_datasets = (
        ensure_datasets_are_ready(db, dataset_ids=in_merge.exclude_datasets) if in_merge.exclude_datasets else None
    )

    task_hash = gen_task_hash(current_user.id, in_merge.project_id)
    try:
        controller_client.merge_datasets(
            current_user.id,
            in_merge.project_id,
            task_hash,
            [d.hash for d in in_datasets] if in_datasets else None,
            [d.hash for d in ex_datasets] if ex_datasets else None,
            in_merge.merge_strategy,
        )
    except ValueError:
        logger.exception("[merge] failed to create merge via controller")
        raise ControllerError()

    task = crud.task.create_placeholder(
        db,
        type_=TaskType.merge,
        user_id=current_user.id,
        project_id=in_merge.project_id,
        hash_=task_hash,
        state_=TaskState.pending,
        parameters=in_merge.json(),
    )
    logger.info("[merge] related task record created: %s", task.hash)
    merged_dataset = crud.dataset.create_as_task_result(
        db, task, main_dataset.dataset_group_id, description=in_merge.description
    )
    return {"result": merged_dataset}


@router.post("/filter", response_model=schemas.dataset.DatasetOut)
def filter_dataset(
    *,
    db: Session = Depends(deps.get_db),
    in_filter: schemas.dataset.DatasetFilterCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Filter dataset
    """
    logger.info("[filter] filter dataset with payload: %s", in_filter.json())
    datasets = ensure_datasets_are_ready(db, dataset_ids=[in_filter.dataset_id])
    main_dataset = datasets[0]

    class_ids = (
        user_labels.get_class_ids(names_or_aliases=in_filter.include_keywords) if in_filter.include_keywords else None
    )
    ex_class_ids = (
        user_labels.get_class_ids(names_or_aliases=in_filter.exclude_keywords) if in_filter.exclude_keywords else None
    )

    task_hash = gen_task_hash(current_user.id, in_filter.project_id)
    try:
        controller_client.filter_dataset(
            current_user.id,
            in_filter.project_id,
            task_hash,
            main_dataset.hash,
            class_ids,
            ex_class_ids,
            in_filter.sampling_count,
        )
    except ValueError:
        logger.exception("[filter] failed to create filter via controller")
        raise ControllerError()

    task = crud.task.create_placeholder(
        db,
        type_=TaskType.filter,
        user_id=current_user.id,
        project_id=in_filter.project_id,
        hash_=task_hash,
        state_=TaskState.pending,
        parameters=in_filter.json(),
    )
    logger.info("[filter] related task record created: %s", task.hash)
    filtered_dataset = crud.dataset.create_as_task_result(
        db, task, main_dataset.dataset_group_id, description=in_filter.description
    )
    return {"result": filtered_dataset}
