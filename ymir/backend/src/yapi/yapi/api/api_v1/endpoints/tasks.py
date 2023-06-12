from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Path, File, UploadFile
from fastapi.logger import logger

from yapi import schemas
from yapi.api import deps
from yapi.config import settings
from yapi.constants.state import TaskType
from yapi.utils.data import dump_to_json
from yapi.utils.ymir_app import AppClient, must_get_model_stage_id

router = APIRouter()


@router.get("/", response_model=schemas.task.TaskPaginationOut)
def list_tasks(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    name: str = Query(None, description="search by task name"),
    task: str = Query(None, description="search by task type"),
    state: str = Query(None, description="search by task state"),
    pagination: schemas.common.CommonPaginationParams = Depends(),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/tasks"
    params = {"name": name, "type": task, "state": state, **dump_to_json(pagination)}
    resp_json = app.get(url, params=params).json()
    return resp_json


@router.get("/{task_id}", response_model=schemas.task.TaskOut)
def get_task(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_id: int = Path(...),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/tasks/{task_id}"
    resp_json = app.get(url).json()
    return resp_json


@router.post("/{task_id}/terminate", response_model=schemas.common.Common)
def terminate_task(
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_id: int = Path(...),
    fetch_result: bool = Body(..., embed=True),
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/tasks/{task_id}/terminate"
    params = {"fetch_result": fetch_result}
    resp_json = app.post(url, json=params).json()
    return resp_json


@router.post("/train", response_model=schemas.task.CreateTaskResponse)
def create_training_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.TrainTaskRequest,
) -> Any:
    """
    Create training task
    """
    model_stage_id = (
        must_get_model_stage_id(app, task_in.model_version_id)
        if task_in.model_version_id
        else None
    )

    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(
            type=TaskType.training, model_stage_id=model_stage_id, **task_in.dict()
        )
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/inference", response_model=schemas.task.CreateTaskResponse)
def create_infer_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.InferenceTaskRequest,
) -> Any:
    """
    Create inference task
    """
    model_stage_id = must_get_model_stage_id(app, task_in.model_version_id)
    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(
            type=TaskType.dataset_infer, model_stage_id=model_stage_id, **task_in.dict()
        )
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/mine", response_model=schemas.task.CreateTaskResponse)
def create_mine_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.MineTaskRequest,
) -> Any:
    """
    Create mining task
    """
    model_stage_id = must_get_model_stage_id(app, task_in.model_version_id)
    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(
            type=TaskType.mining, model_stage_id=model_stage_id, **task_in.dict()
        )
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/import_dataset", response_model=schemas.task.CreateResourceResponse)
def create_import_dataset_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.ImportDatasetRequest,
) -> Any:
    """
    Import Dataset via copy or url
    """
    url = f"{settings.APP_URL_PREFIX}/datasets/importing/"
    payload = dump_to_json(schemas.task.AppImportOpsAdapter(**task_in.dict()))
    resp = app.post(url, json=payload)
    dataset = resp.json()
    return dataset


@router.post("/import_dataset_file", response_model=schemas.task.CreateResourceResponse)
def create_import_dataset_file_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    file: UploadFile = File(...),
    project_id: int = Body(...),
) -> Any:
    """
    Import Dataset via Uploading file
    """
    resp = app.post(
        f"{settings.APP_URL_PREFIX}/uploadfile/", files={"file": file.file.read()}
    )
    hosted_url = resp.json()["result"]
    logger.info("hosted url: %s", hosted_url)

    url = f"{settings.APP_URL_PREFIX}/datasets/importing/"
    payload = dump_to_json(
        schemas.task.AppImportOpsAdapter(input_url=hosted_url, project_id=project_id)
    )
    resp = app.post(url, json=payload)
    dataset = resp.json()
    return dataset


@router.post("/import_model", response_model=schemas.task.CreateResourceResponse)
def create_import_model_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.ImportModelRequest,
) -> Any:
    """
    Import Model via copy or url
    """
    url = f"{settings.APP_URL_PREFIX}/models/importing/"
    payload = dump_to_json(schemas.task.AppImportOpsAdapter(**task_in.dict()))
    resp = app.post(url, json=payload)
    model = resp.json()
    return model


@router.post("/import_model_file", response_model=schemas.task.CreateResourceResponse)
def create_import_model_file_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    file: UploadFile = File(...),
    project_id: int = Body(...),
) -> Any:
    """
    Import Model via Uploading file
    """
    resp = app.post(
        f"{settings.APP_URL_PREFIX}/uploadfile/", files={"file": file.file.read()}
    )
    hosted_url = resp.json()["result"]
    logger.info("hosted url: %s", hosted_url)

    url = f"{settings.APP_URL_PREFIX}/models/importing/"
    payload = dump_to_json(
        schemas.task.AppImportOpsAdapter(input_url=hosted_url, project_id=project_id)
    )
    resp = app.post(url, json=payload)
    model = resp.json()
    return model


@router.post("/label", response_model=schemas.task.CreateTaskResponse)
def create_label_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.LabelDatasetRequest,
) -> Any:
    """
    Create label task
    """
    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(type=TaskType.label, **task_in.dict())
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/merge_datasets", response_model=schemas.task.CreateTaskResponse)
def create_merge_datasets_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.MergeDatasetsRequest,
) -> Any:
    """
    Create merge datasets task
    """
    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(type=TaskType.merge, **task_in.dict())
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/exclude_datasets", response_model=schemas.task.CreateTaskResponse)
def create_exclude_datasets_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.ExcludeDatasetsRequest,
) -> Any:
    """
    Create exclude datasets task
    """
    task_in = schemas.task.ExcludeDatasetsRequestHelper(**task_in.dict())
    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(type=TaskType.merge, **task_in.dict())
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/sample_dataset", response_model=schemas.task.CreateTaskResponse)
def create_sample_dataset_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.SampleDatasetRequest,
) -> Any:
    """
    Create sample dataset task
    """
    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(type=TaskType.filter, **task_in.dict())
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/filter_dataset", response_model=schemas.task.CreateTaskResponse)
def create_filter_dataset_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.FilterDatasetRequest,
) -> Any:
    """
    Create filter dataset task
    """
    url = f"{settings.APP_URL_PREFIX}/tasks/"
    app_task_in = dump_to_json(
        schemas.task.AppTaskAdapter(type=TaskType.filter, **task_in.dict())
    )
    resp = app.post(url, json=app_task_in)
    task = resp.json()
    return task


@router.post("/import_docker_image", response_model=schemas.task.CreateTaskResponse)
def create_import_docker_image_task(
    *,
    app: AppClient = Depends(deps.get_app_client),
    current_user: schemas.user.UserInfo = Depends(deps.get_current_active_user),
    task_in: schemas.task.ImportDockerImageRequest,
) -> Any:
    url = f"{settings.APP_URL_PREFIX}/images/"
    resp = app.post(url, json={"url": task_in.url, "name": task_in.url.split("/")[-1]})
    task = resp.json()
    logger.info("import docker image task result: %s", task)
    return task
