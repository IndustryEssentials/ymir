from functools import wraps
from typing import Any, Callable, Dict, Optional

from mir.tools.errors import MirRuntimeError

from id_definition.error_codes import VizErrorCode
from src.libs import utils
from src.swagger_models import DatasetEvaluationResult


class VizException(Exception):
    status_code = 400
    code = VizErrorCode.GENERAL_ERROR
    message = "Exception Occured"

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        code: Optional[int] = None,
    ):
        super().__init__()
        self.status_code = status_code or self.status_code
        self.code = code or self.code
        self.message = message or self.message

    def __str__(self) -> str:
        return f"error_code: {self.code}, message: {self.message}"

    def to_dict(self) -> Dict:
        return {
            "status_code": self.status_code,
            "code": self.code,
            "message": self.message,
        }


class BranchNotExists(VizException):
    code = VizErrorCode.BRANCH_NOT_EXISTS
    message = "branch not found"


class ModelNotExists(VizException):
    code = VizErrorCode.MODEL_NOT_EXISTS
    message = "model not found"


class DatasetEvaluationNotExists(VizException):
    code = VizErrorCode.DATASET_EVALUATION_NOT_EXISTS
    message = "dataset evaluation not found"


def catch_viz_exceptions(f: Callable) -> Any:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: dict) -> Any:
        code: int
        message: str
        result: dict

        try:
            return f(*args, **kwargs)
        except VizException as e:
            code = e.code
            message = e.message
            result = {}
        except MirRuntimeError as e:
            code = e.error_code
            message = e.error_message
            result = {}
        except Exception as e:
            code = VizErrorCode.GENERAL_ERROR
            message = str(e)
            result = {}

        resp = utils.suss_resp(code=code, message=message, result=result)
        return DatasetEvaluationResult(**resp)
    return wrapper
