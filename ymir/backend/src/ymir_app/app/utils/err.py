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


def retry(func: Callable, n_times: int = 3, wait: float = 0, backoff: bool = False) -> Any:
    """
    try function for at most n_times.
    if backoff is enabled, wait for wait * 1, wait * 2, ... each time
    """
    for i in range(1, n_times):
        try:
            return func()
        except Exception:
            if wait > 0:
                if backoff:
                    wait = wait * i
                time.sleep(wait)
    logger.error(f"Retry failed after {n_times} {func} attempted")
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
