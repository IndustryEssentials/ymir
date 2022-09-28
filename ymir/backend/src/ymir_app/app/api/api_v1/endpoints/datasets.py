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
    DatasetGroupNotFound,
    DatasetNotFound,
    DuplicateDatasetGroupError,
    NoDatasetPermission,
    FailedToHideProtectedResources,
    FailedToParseVizResponse,
    ProjectNotFound,
    MissingOperations,
    RefuseToProcessMixedOperations,
    RequiredFieldMissing,
)
from app.config import settings
from app.constants.state import TaskState, TaskType, ResultState
from app.utils.iteration import get_iteration_context_converter
from app.utils.ymir_controller import ControllerClient, gen_task_hash
from app.utils.ymir_viz import VizClient
from app.schemas.dataset import MergeStrategy
from app.libs.datasets import (
    import_dataset_in_background,
    evaluate_datasets,
    ensure_datasets_are_ready,
    send_keywords_metrics,
)
from common_utils.labels import UserLabels

router = APIRouter()


@router.get("/batch", response_model=schemas.DatasetsAnalysesOut)
def batch_get_datasets(
    db: Session = Depends(deps.get_db),
    viz_client: VizClient = Depends(deps.get_viz_client),
    project_id: int = Query(...),
    dataset_ids: str = Query(..., example="1,2,3", alias="ids", min_length=1),
    require_ck: bool = Query(False, alias="ck"),
    require_hist: bool = Query(False, alias="hist"),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    ids = [int(i) for i in dataset_ids.split(",")]
    datasets = crud.dataset.get_multi_by_ids(db, ids=ids)
    if len(ids) != len(datasets):
        raise DatasetNotFound()

    datasets_info = [schemas.dataset.DatasetInDB.from_orm(dataset).dict() for dataset in datasets]
    if require_ck or require_hist:
        viz_client.initialize(user_id=current_user.id, project_id=project_id, user_labels=user_labels)
        for dataset in datasets_info:
            if dataset["result_state"] != ResultState.ready:
                continue
            if require_ck:
                dataset_extra_info = viz_client.get_dataset_info(dataset["hash"])
            elif require_hist:
                dataset_extra_info = viz_client.get_dataset_analysis(dataset["hash"], require_hist=True)
            dataset.update(dataset_extra_info)
    return {"result": datasets_info}


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
    response_model=schemas.DatasetInfoOut,
    responses={404: {"description": "Dataset Not Found"}},
)
def get_dataset(
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    keywords_for_negative_info: str = Query(None, alias="keywords"),
    verbose_info: bool = Query(False, alias="verbose"),
    current_user: models.User = Depends(deps.get_current_active_user),
    viz_client: VizClient = Depends(deps.get_viz_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Get verbose information of specific dataset
    """
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()

    keyword_ids: Optional[List[int]] = None
    if keywords_for_negative_info:
        keywords = keywords_for_negative_info.split(",")
        keyword_ids = user_labels.id_for_names(names=keywords, raise_if_unknown=True)[0]

    dataset_info = schemas.dataset.DatasetInDB.from_orm(dataset).dict()
    if verbose_info or keyword_ids:
        viz_client.initialize(
            user_id=current_user.id,
            project_id=dataset.project_id,
            user_labels=user_labels,
        )
        try:
            if verbose_info:
                # get cks and tags
                dataset_stats = viz_client.get_dataset_info(dataset_hash=dataset.hash)
            else:
                # get negative info based on given keywords
                dataset_stats = viz_client.get_dataset_analysis(
                    dataset_hash=dataset.hash, keyword_ids=keyword_ids, require_hist=False
                )
        except ValueError:
            logger.exception("[dataset info] could not convert class_id to class_name, return with basic info")
            pass
        except FailedToParseVizResponse:
            logger.exception("[dataset info] could not get dataset info from viewer, return with basic info")
            pass
        else:
            dataset_info.update(dataset_stats)

    return {"result": dataset_info}


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
    keywords_str: Optional[str] = Query(None, example="person,cat", alias="keywords"),
    cm_types_str: Optional[str] = Query(None, example="tp,mtp", alias="cm_types"),
    cks_str: Optional[str] = Query(None, example="shenzhen,shanghai", alias="cks"),
    tags_str: Optional[str] = Query(None, example="big,small", alias="tags"),
    annotation_types_str: Optional[str] = Query(None, example="gt,pred", alias="annotation_types"),
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

    keywords = keywords_str.split(",") if keywords_str else None
    keyword_ids = user_labels.id_for_names(names=keywords, raise_if_unknown=True)[0] if keywords else None

    viz_client.initialize(
        user_id=current_user.id,
        project_id=dataset.project_id,
        user_labels=user_labels,
    )
    assets = viz_client.get_assets(
        dataset_hash=dataset.hash,
        keyword_ids=keyword_ids,
        cm_types=stringtolist(cm_types_str),
        cks=stringtolist(cks_str),
        tags=stringtolist(tags_str),
        annotation_types=stringtolist(annotation_types_str),
        limit=limit,
        offset=offset,
    )
    return {"result": assets}


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
        user_labels=user_labels,
    )
    assets = viz_client.get_assets(
        dataset_hash=dataset.hash,
        keyword_id=None,
        offset=offset,
        limit=1,
    )
    if assets["total"] == 0:
        raise AssetNotFound()
    return {"result": assets["items"][0]}


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
        user_labels=user_labels,
    )
    assets = viz_client.get_assets(dataset_hash=dataset.hash, asset_hash=asset_hash, limit=1)
    if assets["total"] == 0:
        raise AssetNotFound()
    return {"result": assets["items"][0]}


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
        "include_class_ids": user_labels.id_for_names(names=fusion_params.include_labels, raise_if_unknown=True)[0],
        "exclude_class_ids": user_labels.id_for_names(names=fusion_params.exclude_labels, raise_if_unknown=True)[0],
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

    if parameters.get("include_class_ids"):
        # update keywords usage metrics when necessary
        send_keywords_metrics(
            current_user.id,
            in_fusion.project_id,
            task.hash,
            parameters["include_class_ids"],
            int(task.create_datetime.timestamp()),
        )

    return {"result": fused_dataset}


@router.post("/evaluation", response_model=schemas.dataset.DatasetEvaluationOut)
def batch_evaluate_datasets(
    *,
    db: Session = Depends(deps.get_db),
    in_evaluation: schemas.dataset.DatasetEvaluationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    evaluate datasets by themselves
    """
    logger.info("[evaluate] evaluate datasets with payload: %s", in_evaluation.json())
    datasets = ensure_datasets_are_ready(db, dataset_ids=in_evaluation.dataset_ids)
    dataset_id_mapping = {dataset.hash: dataset.id for dataset in datasets}

    evaluations = evaluate_datasets(
        controller_client,
        current_user.id,
        in_evaluation.project_id,
        user_labels,
        in_evaluation.confidence_threshold,
        in_evaluation.iou_threshold,
        in_evaluation.require_average_iou,
        in_evaluation.need_pr_curve,
        in_evaluation.main_ck,
        dataset_id_mapping,
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
    duplicated_stats = viz_client.check_duplication([dataset.hash for dataset in datasets])
    duplicated_asset_count = duplicated_stats["duplication"]
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
    if in_merge.dest_group_name:
        if crud.dataset_group.is_duplicated_name_in_project(
            db, project_id=in_merge.project_id, name=in_merge.dest_group_name
        ):
            raise DuplicateDatasetGroupError()
        dest_group = crud.dataset_group.create_dataset_group(
            db,
            name=in_merge.dest_group_name,
            user_id=current_user.id,
            project_id=in_merge.project_id,
        )
    elif in_merge.dest_group_id:
        dest_group = crud.dataset_group.get(db, id=in_merge.dest_group_id)  # type: ignore
        if not dest_group:
            raise DatasetGroupNotFound()
    else:
        raise RequiredFieldMissing()

    in_datasets = ensure_datasets_are_ready(db, dataset_ids=in_merge.include_datasets)
    in_datasets.sort(
        key=attrgetter("create_datetime"),
        reverse=(in_merge.merge_strategy == MergeStrategy.prefer_newest),
    )
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

    merged_dataset = crud.dataset.create_as_task_result(db, task, dest_group.id, description=in_merge.description)
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
        user_labels.id_for_names(names=in_filter.include_keywords, raise_if_unknown=True)[0]
        if in_filter.include_keywords
        else None
    )
    ex_class_ids = (
        user_labels.id_for_names(names=in_filter.exclude_keywords, raise_if_unknown=True)[0]
        if in_filter.exclude_keywords
        else None
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
    if class_ids:
        # update keywords usage metrics when necessary
        send_keywords_metrics(
            current_user.id,
            in_filter.project_id,
            task.hash,
            class_ids,
            int(task.create_datetime.timestamp()),
        )
    return {"result": filtered_dataset}


def stringtolist(s: Optional[str]) -> Optional[List]:
    if s is None:
        return s
    return s.split(",")
