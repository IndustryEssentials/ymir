from typing import Optional

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from id_definition.error_codes import MonitorErrorCode


class APIError(HTTPException):
    status_code = 400
    code = MonitorErrorCode.general_error
    message = "General Error"

    def __init__(self, message: Optional[str] = None, status_code: int = None, code: Optional[int] = None) -> None:
        self.status_code = status_code or self.status_code
        self.message = message or self.message
        self.code = code or self.code

        super().__init__(status_code=self.status_code, detail={"code": self.code, "message": self.message})


class DuplicateTaskIDError(APIError):
    code = MonitorErrorCode.duplicate_task_id
    message = "task_id already exists"


class LogFileError(APIError):
    code = MonitorErrorCode.percent_log_error
    message = "log file error"


def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc, APIError):
        detail = exc.detail
    else:
        detail = {  # type: ignore
            "errors": exc.detail,
            "code": MonitorErrorCode.internal_error,
            "message": "Unknown Error",
        }
    return JSONResponse(detail, exc.status_code)
