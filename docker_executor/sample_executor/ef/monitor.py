from enum import IntEnum
import logging
import time
import traceback

from ef import env


class _TaskState(IntEnum):
    RUNNING = 2
    ERROR = 4


def write_logger(info: str, percent: float = None, exception: Exception = None) -> None:
    logging.info(info)

    if percent is not None or exception is not None:
        _write_monitor_file(info, percent, exception)


def _write_monitor_file(info: str, percent: float = None, exception: Exception = None) -> None:
    env_config = env.get_current_env()
    with open(env_config.output.monitor_file, 'w') as f:
        if not exception:
            state = _TaskState.RUNNING.value
            tb = ''
        else:
            state = _TaskState.ERROR.value
            percent = 1.0
            tb = ''.join(traceback.format_stack()[:-2])  # ignore the last 2 items: write_logger and _write_monitor_file

        f.write(f"{env_config.task_id}\t{time.time()}\t{percent:.2f}\t{state}\t{info}\n")
        f.write(f"{tb}")
