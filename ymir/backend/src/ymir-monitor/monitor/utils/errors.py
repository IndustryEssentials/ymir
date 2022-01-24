from typing import Any, Dict, Optional

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


class APIError(HTTPException):
    status_code = 400
    code = 150400
    message = "General Client Error"

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


class DuplicateTaskIDError(APIError):
    code = 150401
    message = "task_id already exists"


class LogFileError(APIError):
    code = 150402
    message = "log file error"


def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc, APIError):
        detail = exc.detail
    else:
        detail = {  # type: ignore
            "errors": exc.detail,
            "code": 150500,
            "message": "Unknown Error",
        }
    return JSONResponse(detail, exc.status_code)
