from abc import ABC, abstractmethod
from functools import wraps
import logging
import time
from typing import Any, Dict, Callable


def time_it(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: Dict) -> Callable:
        _start = time.time()
        _ret = f(*args, **kwargs)
        _cost = time.time() - _start
        logging.info(f"|-{f.__name__} costs {_cost:.2f}s({_cost / 60:.2f}m).")
        return _ret

    return wrapper


class BaseCommand(ABC):
    """base class for all commands in mir"""

    # lifecycle
    def __init__(self, args: Any):
        self.args = args

    @time_it
    def cmd_run(self) -> int:
        return self.run()

    @abstractmethod
    def run(self) -> int:
        logging.critical("BaseCommand run: this action should override in sub classes")
        return 0
