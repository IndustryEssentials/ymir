import logging
import time
from functools import wraps
from typing import Dict, Callable

from flask import request


def suss_resp(code: int = 0, message: str = "operation successful", result: Dict = {}) -> Dict:
    resp = dict(
        code=code,
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
        logging.info(f"|-{f.__name__} costs {_cost:.2f}s({_cost / 60:.2f}m).")
        return _ret

    return wrapper
