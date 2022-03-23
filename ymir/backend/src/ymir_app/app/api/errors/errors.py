from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.config import settings
from id_definition.error_codes import APIErrorCode as error_codes


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc, APIError):
        detail = exc.detail
    else:
        detail = {  # type: ignore
            "errors": exc.detail,
            "code": error_codes.UNKNOWN_ERROR,
            "message": "Unknown Error",
        }
    return JSONResponse(detail, status_code=200 if settings.USE_200_EVERYWHERE else exc.status_code)


async def http422_error_handler(
    _: Request,
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    return JSONResponse(
        {
            "code": error_codes.VALIDATION_FAILED,
            "message": "Invalid Request Format",
            "errors": exc.errors(),
        },
        status_code=200 if settings.USE_200_EVERYWHERE else HTTP_422_UNPROCESSABLE_ENTITY,
    )


class APIError(HTTPException):
    status_code = 400
    code = error_codes.API_ERROR
    message = "General API Error"

    def __init__(
        self,
        status_code: int = None,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        status_code = status_code or self.status_code
        detail = detail or {"code": self.code, "message": self.message}
        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers


class IncorrectEmailOrPassword(APIError):
    code = error_codes.INCORRECT_EMAIL_OR_PASSWORD
    message = "Incorrect email or password"


class NotFound(APIError):
    status_code = 404


class FailedtoDownloadError(APIError):
    code = error_codes.FAILED_TO_DOWNLOAD
    message = "Failed to Download"


class ControllerError(APIError):
    code = error_codes.CONTROLLER_ERROR
    message = "General Controller Error"


class FailedtoCreateTask(ControllerError):
    code = error_codes.TASK_FAILED_TO_CREATE
    message = "Failed to Create Task via Controller"


class FailedToCallInference(ControllerError):
    code = error_codes.INFERENCE_FAILED_TO_CALL
    message = "Failed to Create Task via Controller"


class InvalidInferenceConfig(APIError):
    code = error_codes.INFERENCE_CONFIG_ERROR
    message = "Invalid Inference Model Config"


class FailedtoCreateDataset(ControllerError):
    code = error_codes.DATASET_FAILED_TO_CREATE
    message = "Failed to Create Dataset via Controller"


class FailedtoCreateModel(ControllerError):
    code = error_codes.MODEL_FAILED_TO_CREATE
    message = "Failed to Create Model via Controller"


class RequiredFieldMissing(APIError):
    code = error_codes.REQUIRED_FIELD_MISSING
    message = "Required Field Missing"


class InvalidConfiguration(APIError):
    code = error_codes.INVALID_CONFIGURATION
    message = "API Configuration Error"


class FieldValidationFailed(APIError):
    code = error_codes.VALIDATION_FAILED
    message = "Field Validation Failed"


class UserNotFound(NotFound):
    code = error_codes.USER_NOT_FOUND
    message = "User Not Found"


class TaskNotFound(NotFound):
    code = error_codes.TASK_NOT_FOUND
    message = "Task Not Found"


class DatasetNotFound(NotFound):
    code = error_codes.DATASET_NOT_FOUND
    message = "Dataset Not Found"


class AssetNotFound(NotFound):
    code = error_codes.ASSET_NOT_FOUND
    message = "Asset Not Found"


class ModelNotFound(NotFound):
    code = error_codes.MODEL_NOT_FOUND
    message = "Model Not Found"


class ModelNotReady(APIError):
    code = error_codes.MODEL_NOT_READY
    message = "Model Not Ready"


class GraphNotFound(NotFound):
    code = error_codes.GRAPH_NOT_FOUND
    message = "Graph Not Found"


class DockerImageNotFound(NotFound):
    code = error_codes.DOCKER_IMAGE_NOT_FOUND
    message = "Docker Image Not Found"


class PermissionDenied(APIError):
    status_code = 403


class NotEligibleRole(PermissionDenied):
    code = error_codes.USER_ROLE_NOT_ELIGIBLE
    message = "User Role is not Eligible"


class NoDatasetPermission(PermissionDenied):
    code = error_codes.DATASET_NOT_ACCESSIBLE
    message = "No Permission to Access or Modify Dataset"


class NoModelPermission(PermissionDenied):
    code = error_codes.MODEL_NOT_ACCESSIBLE
    message = "No Permission to Access or Modify Model"


class NoTaskPermission(PermissionDenied):
    code = error_codes.TASK_NOT_ACCESSIBLE
    message = "No Permission to Access or Modify Task"


class UserNotAdmin(APIError):
    status_code = 401
    code = error_codes.USER_NOT_ADMIN
    message = "User is Not Admin"


class InvalidToken(APIError):
    status_code = 401
    code = error_codes.INVALID_TOKEN
    message = "Invalid Token"


class InvalidScope(APIError):
    status_code = 401
    code = error_codes.INVALID_SCOPE
    message = "Invalid Scope"


class InactiveUser(APIError):
    status_code = 401
    code = error_codes.USER_NOT_ACTIVE
    message = "User is Inactive"


class DuplicateError(APIError):
    status_code = 400


class DuplicateUserNameError(DuplicateError):
    code = error_codes.USER_DUPLICATED_NAME
    message = "Duplicated User Name"


class DuplicateDatasetError(DuplicateError):
    code = error_codes.DATASET_DUPLICATED_NAME
    message = "Duplicated Dataset Name"


class DuplicateModelError(DuplicateError):
    code = error_codes.MODEL_DUPLICATED_NAME
    message = "Duplicated Model Name"


class DuplicateTaskError(DuplicateError):
    code = error_codes.TASK_DUPLICATED_NAME
    message = "Duplicated Task Name"


class DuplicateKeywordError(DuplicateError):
    code = error_codes.KEYWORD_DUPLICATED
    message = "Duplicated Keyword"


class DuplicateDockerImageError(DuplicateError):
    code = error_codes.DOCKER_IMAGE_DUPLICATED
    message = "Duplicated Docker Image"


class FailedtoShareDockerImage(APIError):
    code = error_codes.FAILED_TO_SHARE_DOCKER_IMAGE
    message = "Failed to Share Docker Image"


class FailedtoGetSharedDockerImages(APIError):
    code = error_codes.FAILED_TO_GET_SHARED_DOCKER_IMAGES
    message = "Failed to Share Docker Image"


class InvalidSharedImageConfig(APIError):
    code = error_codes.SHARED_IMAGE_CONFIG_ERROR
    message = "Invalid Shared Image Config"


class DockerImageHavingRelationships(APIError):
    code = error_codes.DOCKER_IMAGE_HAVING_RELATIONSHIPS
    message = "Docker Image Has Reminding Relationships"


class FailedtoGetSysInfo(ControllerError):
    code = error_codes.FAILED_TO_GET_SYS_INFO
    message = "Failed to Get Sys Info"


class ObsoleteTaskStatus(APIError):
    code = error_codes.TASK_STATUS_OBSOLETE
    message = "Obsolete Task Status"


class FailedToUpdateTaskStatus(APIError):
    code = error_codes.FAILED_TO_UPDATE_TASK_STATUS
    message = "Failed to Update Task Status"


class FailedToConnectClickHouse(APIError):
    code = error_codes.FAILED_TO_CONNECT_CLICKHOUSE
    message = "Failed to Connect ClickHouse"


class FailedToCreateProject(APIError):
    code = error_codes.PROJECT_FAILED_TO_CREATE
    message = "Failed to Create Project"


class ProjectNotFound(NotFound):
    code = error_codes.PROJECT_NOT_FOUND
    message = "Project Not Found"


class DuplicateProjectError(DuplicateError):
    code = error_codes.PROJECT_DUPLICATED_NAME
    message = "Duplicated Project Name"


class DatasetGroupNotFound(NotFound):
    code = error_codes.DATASET_GROUP_NOT_FOUND
    message = "DatasetGroup Not Found"


class DuplicateDatasetGroupError(DuplicateError):
    code = error_codes.DATASET_GROUP_DUPLICATED_NAME
    message = "Duplicated DatasetGroup Name"


class ModelGroupNotFound(NotFound):
    code = error_codes.MODEL_GROUP_NOT_FOUND
    message = "ModelGroup Not Found"


class DuplicateModelGroupError(DuplicateError):
    code = error_codes.MODEL_GROUP_DUPLICATED_NAME
    message = "Duplicated ModelGroup Name"


class FailedToCreateUser(APIError):
    code = error_codes.USER_FAILED_TO_CREATE
    message = "Failed to Create User"


class FailedtoImportModel(APIError):
    code = error_codes.FAILED_TO_IMPORT_MODEL
    message = "Failed to Import Model"


class FailedToCreateIteration(APIError):
    code = error_codes.ITERATION_FAILED_TO_CREATE
    message = "Failed to Create Iteration"


class IterationNotFound(NotFound):
    code = error_codes.ITERATION_NOT_FOUND
    message = "Iteration Not Found"


class FailedToUpdateIterationStage(APIError):
    code = error_codes.ITERATION_COULD_NOT_UPDATE_STAGE
    message = "Failed to Update Iteration Stage"
