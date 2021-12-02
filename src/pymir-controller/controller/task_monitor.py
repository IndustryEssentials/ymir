import logging
import multiprocessing as mp
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import yaml
from google.protobuf import json_format

from controller.utils import singleton, tasks_util
from proto import backend_pb2


class _ScheduledProcess(mp.Process):
    __slots__ = ("_seconds", "_function", "_args", "_kwargs", "_scheduled_event")

    def __init__(self, seconds: float, function: Callable, *args: tuple, **kwargs: Dict[str, Any]):
        super(_ScheduledProcess, self).__init__(target=self._peridically_worker)
        self._seconds = seconds
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self._scheduled_event = mp.Event()

    def _peridically_worker(self) -> None:
        while not self._scheduled_event.wait(self._seconds):
            self._function(*self._args, **self._kwargs)
        self._scheduled_event.set()

    def cancel(self) -> None:
        self._scheduled_event.set()


@singleton.singleton
class ControllerTaskMonitor:
    def __init__(self, storage_root: str) -> None:
        self._task_manager = mp.Manager()
        self._task_storage = self._task_manager.dict()  # type: Dict[str, str]
        self._monitor_process = None  # type: Optional[_ScheduledProcess]
        self._task_interval = 30

        if not os.path.isdir(storage_root):
            raise RuntimeError("Invalid storage_root: {}".format(storage_root))
        self._storage_root = storage_root
        self._task_storage_file = os.path.join(storage_root, "task_storage.yaml")
        self.load_tasks()

        self._start_monitor()

    def load_tasks(self) -> None:
        if os.path.isfile(self._task_storage_file):
            with open(self._task_storage_file) as f:
                storage_yaml = yaml.safe_load(f)
            for task_id, task_monitor_file in storage_yaml.items():
                self._task_storage[task_id] = task_monitor_file

    def save_tasks(self) -> None:
        with open(self._task_storage_file, 'w') as outfile:
            yaml.dump(dict(self._task_storage), outfile)

    def save_task(self, task_id: str, task_storage_item: backend_pb2.TaskMonitorStorageItem) -> None:
        storage_dict = json_format.MessageToDict(task_storage_item,
                                                 preserving_proto_field_name=True,
                                                 use_integers_for_enums=True)
        task_storage_file = self._task_file_location(task_id)
        with open(task_storage_file, 'w') as f:
            yaml.dump(storage_dict, f)

    def load_task(self, task_id: str) -> backend_pb2.TaskMonitorStorageItem:
        task_storage_file = self._task_file_location(task_id)
        task_storage_item = backend_pb2.TaskMonitorStorageItem()
        if not os.path.isfile(task_storage_file):
            logging.error("task storage file not ready: {}".format(task_id))
        else:
            with open(task_storage_file) as f:
                storage_dict = yaml.safe_load(f)
            json_format.ParseDict(storage_dict, task_storage_item, ignore_unknown_fields=False)
        return task_storage_item

    def _monitor_process_func(self) -> None:
        # for each task in `self._task_storage`:
        #   update state according to corresponding monitor file.
        finished_task_ids = set()
        for task_id, task_monitor_file in self._task_storage.items():
            if not os.path.isfile(task_monitor_file):
                logging.warning("cannot find task_monitor_file: {}".format(task_monitor_file))
                continue  # cannt find task file.

            task_item = self._update_task_item(task_monitor_file, task_id)
            if task_item.state in [backend_pb2.TaskStateDone, backend_pb2.TaskStateError]:
                logging.debug("monitor found finished task: %s, state: %s", task_id, task_item.state)
                finished_task_ids.add(task_id)
        for task_id in finished_task_ids:
            del self._task_storage[task_id]

        self.save_tasks()

    def _update_task_item(self, task_monitor_file: str, task_id: str) -> backend_pb2.TaskMonitorStorageItem:
        task_storage_item = self.load_task(task_id=task_id)
        task_item = task_storage_item.general_info

        monitor_file_lines = []
        if os.path.isfile(task_monitor_file):
            with open(task_monitor_file, "r") as f:
                monitor_file_lines = f.readlines()
        if not monitor_file_lines or len(monitor_file_lines[0]) < 4:
            task_item.update_timestamp = int(datetime.now().timestamp())
            task_item.state = backend_pb2.TaskStateUnknown
            task_item.last_error = "invalid monitor file: {}".format(task_monitor_file)
        else:
            content_row_one = monitor_file_lines[0].strip().split("\t")
            task_id, timestamp, percent, state, *_ = content_row_one
            if task_id != task_item.task_id:
                raise ValueError("wrong task id: {0} vs. {1}".format(task_id, task_item.task_id))
            if task_item.update_timestamp == int(timestamp):  # nothing to update
                return task_item
            if len(content_row_one) > 4:
                task_item.state_code = content_row_one[4]
            if len(content_row_one) > 5:
                task_item.state_message = content_row_one[5]

            task_item.update_timestamp = int(timestamp)
            task_item.percent = float(percent)
            task_item.state = tasks_util.task_state_str_to_code(state)
            # error messages
            if len(monitor_file_lines) > 1:
                task_item.last_error = "\n".join(monitor_file_lines[1:100])

        self.save_task(task_id=task_id, task_storage_item=task_storage_item)
        return task_item

    def _task_file_location(self, task_id: str) -> str:
        if not self._storage_root:
            raise RuntimeError("not initialized yet")
        if not os.path.isdir(self._storage_root):
            raise RuntimeError("storage_root {} not exist".format(self._storage_root))
        return os.path.join(self._storage_root, task_id + '.yaml')

    def _start_monitor(self) -> None:
        if self._monitor_process:
            return  # if already started, does nothing
        self._monitor_process = _ScheduledProcess(self._task_interval, self._monitor_process_func)
        self._monitor_process.start()

    def stop_monitor(self) -> None:
        if not self._monitor_process:
            return
        self._monitor_process.cancel()
        self._monitor_process = None

    def _generate_storage_item(self, task_id: str, repo_root: str, task_monitor_file: str,
                               request: backend_pb2.GeneralReq) -> backend_pb2.TaskMonitorStorageItem:
        general_info = backend_pb2.TaskInfoItem()
        general_info.task_id = task_id
        general_info.user_id = request.user_id
        general_info.repo_id = request.repo_id
        general_info.type = request.req_type
        general_info.state = backend_pb2.TaskStatePending
        general_info.start_timestamp = int(datetime.now().timestamp())
        general_info.percent = 0

        task_storage_item = backend_pb2.TaskMonitorStorageItem()
        task_storage_item.general_info.CopyFrom(general_info)
        task_storage_item.monitor_file_path = task_monitor_file
        task_storage_item.storage_file_path = self._task_file_location(task_id)
        task_storage_item.repo_root = repo_root
        task_storage_item.branch_name = request.dst_task_id
        task_storage_item.request.CopyFrom(request)
        return task_storage_item

    def register_task(self, task_id: str, repo_root: str, task_monitor_file: str, request: backend_pb2.GeneralReq) -> None:
        self._start_monitor()  # In case monitor has not been started.

        if task_id in self._task_storage:
            logging.warning("Task {0} already exist.".format(task_id))
            del self._task_storage[task_id]

        tasks_util.write_task_progress(task_monitor_file, task_id, 0, backend_pb2.TaskStatePending)
        task_storage_item = self._generate_storage_item(task_id=task_id,
                                                        repo_root=repo_root,
                                                        task_monitor_file=task_monitor_file,
                                                        request=request)
        self.save_task(task_id=task_id, task_storage_item=task_storage_item)

        self._task_storage[task_id] = task_monitor_file
        self.save_tasks()

    def has_task(self, task_id: str) -> bool:
        return (task_id in self._task_storage) and os.path.isfile(self._task_file_location(task_id))

    # def get_task_info(self, task_id: str) -> Optional[backend_pb2.TaskMonitorStorageItem]:
    #     if not self.has_task(task_id):
    #         return None

    #     task_item = backend_pb2.TaskMonitorStorageItem()
    #     with open(self._task_storage[task_id], 'rb') as f:
    #         task_item.ParseFromString(f.read())
    #     return task_item
