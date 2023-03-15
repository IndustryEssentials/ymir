from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.config import settings
from id_definition.error_codes import APIErrorCode as error_codes, CTLResponseCode as ctl_error_codes


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


class FailedToSendEmail(APIError):
    code = error_codes.FAILED_TO_SEND_EMAIL
    message = "Failed to send email"


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


class FailedtoCreateSegLabelTask(ControllerError):
    code = error_codes.TASK_SEGMENTATION_LABEL_NOT_SUPPORTED
    message = "Failed to Create Segmentation Label Task"


class FailedToCallInference(ControllerError):
    code = error_codes.INFERENCE_FAILED_TO_CALL
    message = "Failed to Create Task via Controller"


class InvalidInferenceResultFormat(ControllerError):
    code = error_codes.INVALID_INFERENCE_RESULT_FORMAT
    message = "Invalid Inference Result Format"


class FailedToTerminateTask(ControllerError):
    code = error_codes.TASK_FAILED_TO_TERMINATE
    message = "Failed to Terminate Task via Controller"


class InvalidInferenceConfig(APIError):
    code = error_codes.INFERENCE_CONFIG_ERROR
    message = "Invalid Inference Model Config"


class FailedtoCreateDataset(ControllerError):
    code = error_codes.DATASET_FAILED_TO_CREATE
    message = "Failed to Create Dataset via Controller"


class FailedtoCreateModel(ControllerError):
    code = error_codes.MODEL_FAILED_TO_CREATE
    message = "Failed to Create Model via Controller"


class FailedToEvaluate(ControllerError):
    code = error_codes.FAILED_TO_EVALUATE
    message = "Failed to RUN EVALUATE CMD via Controller"


class InvalidRepo(ControllerError):
    code = ctl_error_codes.INVALID_MIR_ROOT
    message = "Invalid repo"


class PrematureDatasets(APIError):
    code = error_codes.PREMATURE_DATASETS
    message = "Not All The Datasets Are Ready"


class PrematurePredictions(APIError):
    code = error_codes.PREMATURE_PREDICTIONS
    message = "Not All The Predictions Are Ready"


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


class PredictionNotFound(NotFound):
    code = error_codes.PREDICTION_NOT_FOUND
    message = "Prediction Not Found"


class AssetNotFound(NotFound):
    code = error_codes.ASSET_NOT_FOUND
    message = "Asset Not Found"


class ModelNotFound(NotFound):
    code = error_codes.MODEL_NOT_FOUND
    message = "Model Not Found"


class ModelStageNotFound(NotFound):
    code = error_codes.MODEL_STAGE_NOT_FOUND
    message = "Model Stage Not Found"


class DatasetEvaluationNotFound(NotFound):
    code = error_codes.DATASET_EVALUATION_NOT_FOUND
    message = "Dataset Evaluation Not Found"


class DatasetEvaluationMissingAnnotation(NotFound):
    code = error_codes.DATASET_EVALUATION_NO_ANNOTATIONS
    message = "Could Not Evaluate Dataset Without Annotations"


class DatasetIndexNotReady(APIError):
    code = error_codes.DATASET_INDEX_NOT_READY
    message = "Dataset Index In MongoDB Not Ready"


class ModelNotReady(APIError):
    code = error_codes.MODEL_NOT_READY
    message = "Model Not Ready"


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


class NoPredictionPermission(PermissionDenied):
    code = error_codes.PREDICTION_NOT_ACCESSIBLE
    message = "No Permission to Access or Modify Prediction"


class UserNotAdmin(APIError):
    status_code = 401
    code = error_codes.USER_NOT_ADMIN
    message = "User is Not Admin"


class InvalidToken(APIError):
    status_code = 401
    code = error_codes.INVALID_TOKEN
    message = "Invalid Token"


class SystemVersionConflict(APIError):
    status_code = 401
    code = error_codes.SYSTEM_VERSION_CONFLICT
    message = "System Version Conflict"


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


class DuplicatePhoneError(DuplicateError):
    code = error_codes.USER_DUPLICATED_PHONE
    message = "Duplicated User Phone"


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


class DockerImageHavingRelationships(APIError):
    code = error_codes.DOCKER_IMAGE_HAVING_RELATIONSHIPS
    message = "Docker Image Has Reminding Relationships"


class FailedtoGetSysInfo(ControllerError):
    code = error_codes.FAILED_TO_GET_SYS_INFO
    message = "Failed to Get Sys Info"


class ObsoleteTaskStatus(APIError):
    code = error_codes.TASK_STATUS_OBSOLETE
    message = "Obsolete Task Status"


class FailedToUpdateTaskStatusTemporally(APIError):
    code = error_codes.FAILED_TO_UPDATE_TASK_STATUS
    message = "Failed to Update Task Status"


class FailedToCreateProject(APIError):
    code = error_codes.PROJECT_FAILED_TO_CREATE
    message = "Failed to Create Project"


class ProjectNotFound(NotFound):
    code = error_codes.PROJECT_NOT_FOUND
    message = "Project Not Found"


class InvalidProject(APIError):
    code = error_codes.INVALID_PROJECT
    message = "Invalid Project"


class DuplicateProjectError(DuplicateError):
    code = error_codes.PROJECT_DUPLICATED_NAME
    message = "Duplicated Project Name"


class FailedToHideProtectedResources(APIError):
    code = error_codes.FAILED_TO_PROCESS_PROTECTED_RESOURCES
    message = "Failed to Hide Protected Resources in Project"


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


class DuplicateIterationError(DuplicateError):
    code = error_codes.ITERATION_DUPLICATED
    message = "Duplicate Iteration"


class IterationNotFound(NotFound):
    code = error_codes.ITERATION_NOT_FOUND
    message = "Iteration Not Found"


class FailedToUpdateIterationStage(APIError):
    code = error_codes.ITERATION_COULD_NOT_UPDATE_STAGE
    message = "Failed to Update Iteration Stage"


class IterationStepNotFound(NotFound):
    code = error_codes.ITERATION_STEP_NOT_FOUND
    message = "IterationStep Not Found"


class IterationStepHasFinished(APIError):
    code = error_codes.ITERATION_STEP_ALREADY_FINISHED
    message = "IterationStep Has Finished"


class RefuseToProcessMixedOperations(APIError):
    code = error_codes.REFUSE_TO_PROCESS_MIXED_OPERATIONS
    message = "Refuse To Process Mixed Operations"


class MissingOperations(APIError):
    code = error_codes.MISSING_OPERATIONS
    message = "Missing Operations"


class DatasetsNotInSameGroup(APIError):
    code = error_codes.DATASETS_NOT_IN_SAME_GROUP
    message = "Datasets Not in the Same Group"


class InvalidModelStageName(APIError):
    code = error_codes.INVALID_MODEL_STAGE_NAME
    message = "Invalid Model Stage Name"


class VizError(APIError):
    code = error_codes.VIZ_ERROR
    message = "General Viz Error"


class FailedToParseVizResponse(VizError):
    code = error_codes.FAILED_TO_PARSE_VIZ_RESP
    message = "Failed to Parse Viz Response"


class VizTimeOut(VizError):
    code = error_codes.VIZ_TIMEOUT
    message = "Internal Viz Service Timeout"
