""" write task progress percent """

import datetime
from enum import Enum
from functools import wraps
import json
import math
import os
from subprocess import CalledProcessError
import traceback
from typing import Any, Callable, Dict, List, Optional

from mir.tools.code import MirCode, MirRuntimeError
from mir.tools import revs_parser, mir_repo_utils


class PhaseStateEnum(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    DONE = 'done'
    ERROR = 'error'


class PhaseLogger:
    # life cycle
    def __init__(self,
                 task_name: str,
                 monitor_file: Optional[str] = None,
                 start: float = 0.0,
                 end: float = 1.0,
                 auto_done: bool = False) -> None:
        assert task_name
        assert start >= 0 and start <= 1
        assert end >= 0 and end <= 1
        assert start < end

        self._task_name = task_name
        self._monitor_file = monitor_file
        self._start_percent = start
        self._end_percent = end
        self._local_percent = 0.0  # between 0 and 1
        self.auto_done = auto_done

        if monitor_file:
            monitor_dir_name = os.path.dirname(monitor_file)
            if not os.path.isdir(monitor_dir_name):
                os.makedirs(monitor_dir_name, exist_ok=True)

    # public: properties
    @property
    def task_name(self) -> str:
        return self._task_name

    @property
    def monitor_file(self) -> Optional[str]:
        return self._monitor_file

    @property
    def start_percent(self) -> float:
        return self._start_percent

    @property
    def end_percent(self) -> float:
        return self._end_percent

    @property
    def global_percent(self) -> float:
        return self._start_percent + self._local_percent * (self._end_percent - self._start_percent)

    @property
    def local_percent(self) -> float:
        return self._local_percent

    # public: general
    def update_percent_info(self, local_percent: float, task_state: PhaseStateEnum,
                            state_code: int = 0,
                            state_content: str = None,
                            trace_message: str = None) -> None:
        # if no monitor_file assgned, no need to write monitor percent log
        assert local_percent >= 0 and local_percent <= 1
        self._local_percent = local_percent

        if not self.monitor_file:
            return

        global_percent = min(self.global_percent, 1)

        with open(self.monitor_file, 'w') as f:
            timestamp = int(datetime.datetime.now().timestamp())
            f.write(f"{self.task_name}\t{timestamp}\t{global_percent:.2f}\t{task_state}")
            if state_code and state_content:
                f.write(f"\t{state_code}\t{state_content}")
            f.write("\n")
            if trace_message:
                f.write(f"{trace_message}\n")

    def create_children(self, deltas: List[float]) -> List['PhaseLogger']:
        """
        creates child phase loggers for current period

        for example:
        * a phase logger in period (start=0, end=0) will separate into two sub loggers for delta [0.4, 0.6]:
            * sub logger 1: start=0, end=0.4
            * sub logger 2: start=0.4, end=1
        * a phase logger in period (start=0.1, end=0.8) will separate into two sub loggers for delta [0.4, 0.6]:
            * sub logger 1: start=0.1, end=0.38
            * sub logger 2: start=0.38, end=0.8

        Args:
            deltas (List[float]): separation ratios

        Returns:
            List[PhaseLogger]: child phase loggers
        """
        # check deltas
        total = 0.0
        for d in deltas:
            assert d > 0 and d <= 1
            total += d
        assert math.isclose(total, 1), f"total: {total}"

        start = self.start_percent
        parent_delta = self.end_percent - self.start_percent
        children: List[PhaseLogger] = []
        for d in deltas:
            end = start + d * parent_delta
            children.append(PhaseLogger(task_name=self.task_name, monitor_file=self.monitor_file, start=start, end=end))
            start = end

        return children


class PhaseLoggerCenter:
    _phase_name_to_loggers: Dict[str, PhaseLogger] = {}

    @staticmethod
    def clear_all() -> None:
        if PhaseLoggerCenter._phase_name_to_loggers:
            PhaseLoggerCenter._phase_name_to_loggers = {}

    @staticmethod
    def loggers() -> Dict[str, PhaseLogger]:
        return dict(PhaseLoggerCenter._phase_name_to_loggers)

    @staticmethod
    def create_phase_loggers(top_phase: str, monitor_file: Optional[str], task_name: str) -> None:
        conf_path = os.path.join(os.path.dirname(__file__), 'phase_logger_conf.json')
        with open(conf_path, 'r') as f:
            conf = json.loads(f.read())
        assert top_phase in conf, f"{top_phase} not in {conf}"

        sub_phase_confs = conf[top_phase]
        sub_phase_names = []
        sub_deltas: List[Any] = []
        for sub_phase_conf in sub_phase_confs:
            sub_phase_names.append(sub_phase_conf['name'])
            sub_deltas.append(sub_phase_conf['delta'])

        sub_phase_count = len(sub_phase_names)
        top_logger = PhaseLogger(task_name=task_name, monitor_file=monitor_file)
        sub_phase_loggers = top_logger.create_children(deltas=sub_deltas)
        for idx, (sub_phase_name, sub_phase_logger) in enumerate(zip(sub_phase_names, sub_phase_loggers)):
            if idx == sub_phase_count - 1:  # if last, let whole phase auto done
                sub_phase_logger.auto_done = True
            PhaseLoggerCenter._phase_name_to_loggers[f"{top_phase}.{sub_phase_name}"] = sub_phase_logger

    @staticmethod
    def update_phase(phase: str,
                     local_percent: float = 1,
                     task_state: PhaseStateEnum = PhaseStateEnum.RUNNING,
                     state_code: int = 0,
                     state_content: str = None,
                     trace_message: str = None) -> None:
        if not phase:
            return

        assert phase in PhaseLoggerCenter._phase_name_to_loggers, f"unknown phase: {phase}"

        PhaseLoggerCenter._phase_name_to_loggers[phase].update_percent_info(local_percent=local_percent,
                                                                            task_state=task_state,
                                                                            state_code=state_code,
                                                                            state_content=state_content,
                                                                            trace_message=trace_message)


def phase_logger_in_out(f: Callable) -> Callable:
    """
    decorator for command run_with_args functions for those cmd who wants a PENDING record before f start
        and a DONE / ERROR record after f end

    Args:
        f (Callable): cmd run_with_args functions, should have work_dir and dst_rev in arg list
    """

    def _get_task_name(**kwargs: dict) -> str:
        if 'dst_rev' in kwargs:
            return revs_parser.parse_single_arg_rev(str(kwargs['dst_rev'])).tid
        return 'default-task'

    @wraps(f)
    def wrapper(work_dir: str, *args: tuple, **kwargs: dict) -> Any:
        mir_logger = PhaseLogger(task_name=_get_task_name(**kwargs),
                                 monitor_file=mir_repo_utils.work_dir_to_monitor_file(work_dir))
        mir_logger.update_percent_info(local_percent=0, task_state=PhaseStateEnum.PENDING)

        try:
            ret = f(work_dir=work_dir, *args, **kwargs)
            trace_message = f"cmd return: {ret}"

            if ret == MirCode.RC_OK:
                mir_logger.update_percent_info(local_percent=1, task_state=PhaseStateEnum.DONE)
            else:
                mir_logger.update_percent_info(local_percent=1,
                                               task_state=PhaseStateEnum.ERROR,
                                               state_code=ret,
                                               state_content=trace_message,
                                               trace_message=trace_message)

            return ret
        except MirRuntimeError as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"

            mir_logger.update_percent_info(local_percent=1,
                                           task_state=PhaseStateEnum.ERROR,
                                           state_code=e.error_code,
                                           state_content=e.error_message,
                                           trace_message=trace_message)

            raise e
        except CalledProcessError as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"

            mir_logger.update_percent_info(local_percent=1,
                                           task_state=PhaseStateEnum.ERROR,
                                           state_code=MirCode.RC_RUNTIME_CONTAINER_ERROR,
                                           state_content=str(e),
                                           trace_message=trace_message)

            raise e
        except BaseException as e:
            trace_message = f"cmd exception: {traceback.format_exc()}"
            mir_logger.update_percent_info(local_percent=1,
                                           task_state=PhaseStateEnum.ERROR,
                                           state_code=MirCode.RC_RUNTIME_ERROR_UNKNOWN,
                                           state_content=str(e),
                                           trace_message=trace_message)
            raise e

    return wrapper
