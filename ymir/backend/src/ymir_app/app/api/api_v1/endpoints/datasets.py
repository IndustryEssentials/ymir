from typing import Any, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DatasetGroupNotFound,
    DatasetNotFound,
    DuplicateDatasetGroupError,
    FailedToHideProtectedResources,
    FailedToParseVizResponse,
    ProjectNotFound,
    MissingOperations,
    RefuseToProcessMixedOperations,
)
from app.config import settings
from app.constants.state import TaskState, TaskType, ResultState, ObjectType
from app.utils.ymir_controller import ControllerClient
from app.utils.ymir_viz import VizClient
from app.libs.datasets import import_dataset_in_background, ensure_datasets_are_ready
from app.libs.tasks import create_single_task
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
    ids = list({int(i) for i in dataset_ids.split(",")})
    datasets = crud.dataset.get_multi_by_user_and_ids(db, user_id=current_user.id, ids=ids)
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


@router.get("/", response_model=schemas.DatasetPaginationOut)
def list_datasets(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    source: TaskType = Query(None, description="type of related task"),
    exclude_source: TaskType = Query(None, description="exclude type of related task"),
    project_id: int = Query(None),
    group_id: int = Query(None),
    group_name: str = Query(None),
    visible: bool = Query(True),
    state: ResultState = Query(None),
    object_type: ObjectType = Query(None),
    pagination: schemas.CommonPaginationParams = Depends(),
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
        group_name=group_name,
        source=source,
        exclude_source=exclude_source,
        state=state,
        object_type=object_type,
        visible=visible,
        pagination=pagination,
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
        allow_empty=False,
        pagination=schemas.CommonPaginationParams(limit=None),
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
    # 1. various validation
    project = crud.project.get(db, dataset_import.project_id)
    if not project:
        raise ProjectNotFound()
    object_type = project.object_type

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

    # 3. create dataset group
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
    dataset = crud.dataset.create_with_version(db, obj_in=dataset_in)
    logger.info("[import dataset] dataset record created: %s", dataset.name)

    # 4. run background task
    background_tasks.add_task(
        import_dataset_in_background,
        db,
        controller_client,
        dataset_import,
        current_user.id,
        task.hash,
        object_type,
        dataset.id,
    )
    return {"result": dataset}


@router.delete("/{dataset_id}", response_model=schemas.DatasetOut)
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
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()
    dataset_group_id = dataset.dataset_group_id
    dataset = crud.dataset.soft_remove(db, id=dataset_id)

    # remove dataset group if all dataset is deleted
    _, total = crud.dataset.get_multi_datasets(
        db,
        user_id=current_user.id,
        group_id=dataset_group_id,
        pagination=schemas.CommonPaginationParams(limit=None),
    )
    if not total:
        crud.dataset_group.soft_remove(db, id=dataset_group_id)

    return {"result": dataset}


@router.patch("/{dataset_id}", response_model=schemas.DatasetOut)
def update_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: int = Path(..., example="12"),
    dataset_update: schemas.DatasetUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    dataset = crud.dataset.get_by_user_and_id(db, user_id=current_user.id, id=dataset_id)
    if not dataset:
        raise DatasetNotFound()

    dataset = crud.dataset.update(db, db_obj=dataset, obj_in=dataset_update)
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
        except FailedToParseVizResponse:
            logger.exception("[dataset info] could not get dataset info from viewer, return with basic info")
        else:
            dataset_info.update(dataset_stats)

    return {"result": dataset_info}


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
    datasets = ensure_datasets_are_ready(db, user_id=current_user.id, dataset_ids=in_datasets.dataset_ids)

    viz_client.initialize(user_id=current_user.id, project_id=in_datasets.project_id)
    duplicated_stats = viz_client.check_duplication([dataset.hash for dataset in datasets])
    duplicated_asset_count = duplicated_stats["duplication"]
    return {"result": duplicated_asset_count}


@router.post("/fusion", response_model=schemas.TaskOut)
def create_dataset_fusion_task(
    *,
    db: Session = Depends(deps.get_db),
    in_fusion: schemas.task.FusionParameter,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Create data fusion as a task
    """
    logger.info("[fusion] create dataset fusion with payload: %s", in_fusion.json())

    dataset_group = crud.dataset_group.get(db, id=in_fusion.dataset_group_id)
    if not dataset_group:
        raise DatasetGroupNotFound()

    task_in = schemas.TaskCreate(
        type=TaskType.data_fusion,
        project_id=in_fusion.project_id,
        parameters=in_fusion,
    )
    task_in_db = create_single_task(db, current_user.id, user_labels, task_in)
    return {"result": task_in_db}


@router.post("/merge", response_model=schemas.TaskOut)
def merge_datasets(
    *,
    db: Session = Depends(deps.get_db),
    in_merge: schemas.task.FusionParameter,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Merge multiple datasets
    """
    logger.info("[merge] merge dataset with payload: %s", in_merge.json())

    task_in = schemas.TaskCreate(
        type=TaskType.merge,
        project_id=in_merge.project_id,
        parameters=in_merge,
    )
    task_in_db = create_single_task(db, current_user.id, user_labels, task_in)
    return {"result": task_in_db}


@router.post("/filter", response_model=schemas.TaskOut)
def filter_dataset(
    *,
    db: Session = Depends(deps.get_db),
    in_filter: schemas.task.FusionParameter,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    user_labels: UserLabels = Depends(deps.get_user_labels),
) -> Any:
    """
    Filter dataset
    """
    logger.info("[filter] filter dataset with payload: %s", in_filter.json())

    task_in = schemas.TaskCreate(
        type=TaskType.filter,
        project_id=in_filter.project_id,
        parameters=in_filter,
    )
    task_in_db = create_single_task(db, current_user.id, user_labels, task_in)
    return {"result": task_in_db}
