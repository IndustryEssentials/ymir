from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from auth.config import settings
from .error_codes import APIErrorCode as error_codes


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


class ControllerError(APIError):
    code = error_codes.CONTROLLER_ERROR
    message = "General Controller Error"


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


class PermissionDenied(APIError):
    status_code = 403


class NotEligibleRole(PermissionDenied):
    code = error_codes.USER_ROLE_NOT_ELIGIBLE
    message = "User Role is not Eligible"


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


class FailedToCreateUser(APIError):
    code = error_codes.USER_FAILED_TO_CREATE
    message = "Failed to Create User"
