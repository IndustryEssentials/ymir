import time
from functools import wraps
from typing import Dict, Callable

from flask import request

from src.libs import app_logger


def suss_resp(error_code: int = 0, message: str = "operation successful", result: Dict = {}) -> Dict:
    resp = dict(
        error_code=error_code,
        message=message,
        request_id=request.headers.get("request_id"),
        result=result,
    )

    return resp


def time_it(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: Dict) -> Callable:
        _start = time.time()
        _ret = f(*args, **kwargs)
        _cost = time.time() - _start
        app_logger.logger.info(f"|-{f.__name__} costs {_cost:.2f}s({_cost / 60:.2f}m).")
        return _ret

    return wrapper
