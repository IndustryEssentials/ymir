import functools
import logging
import time
from typing import Any, Callable

import sentry_sdk

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def retry(func: Callable, n_times: int = 3, wait: float = 0) -> Any:
    for i in range(n_times - 1):
        try:
            return func()
        except Exception:
            if wait > 0:
                time.sleep(wait)
    logger.error(f"Error! retry {n_times} {func} also failed ")
    return func()


def catch_error_and_report(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> None:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception("Catched error: %s", e)
            sentry_sdk.capture_exception(e)

    return wrapped
