from enum import IntEnum
import logging
import time
import traceback

from executor import env


class _TaskState(IntEnum):
    RUNNING = 2
    ERROR = 4


def write_monitor_logger(info: str, percent: float = None, error_occured: bool = False) -> None:
    if percent is None and not error_occured:
        raise ValueError('percent and error_occured should not be both none')

    logging.info(info)
    if not error_occured:
        state = _TaskState.RUNNING.value
        tb = ''
    else:
        state = _TaskState.ERROR.value
        percent = 1.0
        # ignore the last 2 items: write_logger and _write_monitor_file
        tb = ''.join(traceback.format_stack()[:-2])

    env_config = env.get_current_env()
    with open(env_config.output.monitor_file, 'w') as f:
        f.write(f"{env_config.task_id}\t{time.time()}\t{percent:.2f}\t{state}\t{info}\n")
        f.write(f"{tb}")
